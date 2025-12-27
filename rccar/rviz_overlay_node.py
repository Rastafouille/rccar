#!/usr/bin/env python3
import rclpy
from rclpy.node import Node

from std_msgs.msg import Float32, Float64, String
from vesc_msgs.msg import VescStateStamped


class RvizOverlayNode(Node):
    def __init__(self):
        super().__init__('rviz_overlay_node')

        # Publishers pour l’overlay
        self.steer_pub = self.create_publisher(Float32, 'rviz_steer', 10)
        self.speed_percent_pub = self.create_publisher(Float32, 'rviz_speed_percent', 10)
        self.speed_pub = self.create_publisher(String, 'rviz_speed', 10)

        # Subscribers aux topics VESC
        self.create_subscription(Float64, '/commands/servo/position', self.steer_callback, 10)
        self.create_subscription(VescStateStamped, '/sensors/core', self.speed_callback, 10)

        # Paramètres "fixes" (tu peux les changer si besoin)
        self.declare_parameter('joy_max_speed', 3.0)
        self.declare_parameter('speed_to_erpm_gain', 1580.0)
        self.declare_parameter('speed_to_erpm_offset', 0.0)
        self.declare_parameter('steering_angle_to_servo_gain', 0.85)
        self.declare_parameter('steering_angle_to_servo_offset', 0.46)

        # Récupération
        self.joy_max_speed = self.get_parameter('joy_max_speed').get_parameter_value().double_value
        self.speed_to_erpm_gain = self.get_parameter('speed_to_erpm_gain').get_parameter_value().double_value
        self.speed_to_erpm_offset = self.get_parameter('speed_to_erpm_offset').get_parameter_value().double_value
        self.steering_angle_to_servo_gain = self.get_parameter('steering_angle_to_servo_gain').get_parameter_value().double_value
        self.steering_angle_to_servo_offset = self.get_parameter('steering_angle_to_servo_offset').get_parameter_value().double_value

        self.get_logger().info("RViz overlay node started ✅")

    def steer_callback(self, msg: Float64):
        steer = Float32()
        steer.data = -100 * (msg.data - self.steering_angle_to_servo_offset) / (self.steering_angle_to_servo_gain * 0.36)
        self.steer_pub.publish(steer)

    def speed_callback(self, msg: VescStateStamped):
        # Pourcentage de la vitesse max
        speed_percent = Float32()
        speed_percent.data = -msg.state.speed / (self.speed_to_erpm_gain * self.joy_max_speed) * 100.0
        self.speed_percent_pub.publish(speed_percent)

        # Vitesse en RPM
        speed_str = String()
        speed_str.data = str(int(-msg.state.speed)) + " RPM"
        self.speed_pub.publish(speed_str)


def main(args=None):
    rclpy.init(args=args)
    node = RvizOverlayNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
