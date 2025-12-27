import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from tf2_ros import TransformBroadcaster, StaticTransformBroadcaster
from geometry_msgs.msg import TransformStamped
import rclpy.parameter


class OdomTFPublisher(Node):
    def __init__(self):
        super().__init__('odom_tf_publisher')

        # IMPORTANT : sim time
        self.set_parameters([
            rclpy.parameter.Parameter(
                'use_sim_time',
                rclpy.Parameter.Type.BOOL,
                True
            )
        ])

        self.sub = self.create_subscription(
            Odometry,
            '/ego_racecar/odom',
            self.odom_callback,
            10
        )

        self.br = TransformBroadcaster(self)
        self.static_br = StaticTransformBroadcaster(self)

        # 🔧 map -> odom (bootstrap)
        static_t = TransformStamped()
        static_t.header.stamp = self.get_clock().now().to_msg()
        static_t.header.frame_id = 'map'
        static_t.child_frame_id = 'ego_racecar/odom'
        static_t.transform.rotation.w = 1.0
        self.static_br.sendTransform(static_t)

        self.get_logger().info("Publishing map -> odom (static)")

    def odom_callback(self, msg):
        t = TransformStamped()
        t.header.stamp = msg.header.stamp
        t.header.frame_id = 'ego_racecar/odom'                     # ⬅️ CRITIQUE
        t.child_frame_id = 'ego_racecar/base_link'     # ⬅️ CRITIQUE

        t.transform.translation.x = msg.pose.pose.position.x
        t.transform.translation.y = msg.pose.pose.position.y
        t.transform.translation.z = msg.pose.pose.position.z
        t.transform.rotation = msg.pose.pose.orientation

        self.br.sendTransform(t)
        self.get_logger().info("Publishing ego_racecar/odom -> ego_racecar/base_link (at %.2f, %.2f)" %(t.transform.translation.x, t.transform.translation.y))



def main():
    rclpy.init()
    node = OdomTFPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
