#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import numpy as np

from sensor_msgs.msg import LaserScan
from ackermann_msgs.msg import AckermannDriveStamped
from visualization_msgs.msg import Marker
from geometry_msgs.msg import Point

class FollowTheGap(Node):
    def __init__(self):
        super().__init__('ftg_node')

        # Params
        self.declare_parameter('scan_topic', '/scan')
        self.declare_parameter('drive_topic', '/drive')
        self.declare_parameter('bubble_radius', 3)    # nb de rayons à bloquer autour des obstacles
        self.declare_parameter('min_range', 0.2)
        self.declare_parameter('max_range', 5.0)
        self.declare_parameter('speed', 1.0)
        self.declare_parameter('safety_distance', 0.5)

        # Topics
        self.scan_sub = self.create_subscription(LaserScan,
                                                 self.get_parameter('scan_topic').value,
                                                 self.scan_callback, 10)
        self.drive_pub = self.create_publisher(AckermannDriveStamped,
                                               self.get_parameter('drive_topic').value, 10)
        self.marker_pub = self.create_publisher(Marker, 'ftg_markers', 10)

        self.get_logger().info("FTG node started")

    def scan_callback(self, scan: LaserScan):
        ranges = np.array(scan.ranges)

        # Nettoyage des ranges
        ranges = np.nan_to_num(ranges, nan=self.get_parameter('max_range').value,
                               posinf=self.get_parameter('max_range').value,
                               neginf=self.get_parameter('min_range').value)
        ranges = np.clip(ranges,
                         self.get_parameter('min_range').value,
                         self.get_parameter('max_range').value)

        # Trouver l'obstacle le plus proche
        min_idx = np.argmin(ranges)
        bubble_radius = self.get_parameter('bubble_radius').value
        ranges[max(0, min_idx-bubble_radius): min(len(ranges), min_idx+bubble_radius)] = 0.0

        # Trouver le plus grand gap
        gaps = []
        in_gap = False
        start = 0
        for i, r in enumerate(ranges):
            if r > self.get_parameter('safety_distance').value and not in_gap:
                in_gap = True
                start = i
            elif r <= self.get_parameter('safety_distance').value and in_gap:
                in_gap = False
                gaps.append((start, i-1))
        if in_gap:
            gaps.append((start, len(ranges)-1))

        if len(gaps) == 0:
            self.get_logger().warn("Pas de gap trouvé → STOP")
            self.publish_drive(0.0, 0.0)
            return

        # Plus grand gap
        best_gap = max(gaps, key=lambda g: g[1]-g[0])
        target_idx = (best_gap[0] + best_gap[1]) // 2
        target_angle = scan.angle_min + target_idx * scan.angle_increment

        # Commande vitesse + steering
        speed = self.get_parameter('speed').value
        steering_angle = target_angle
        self.publish_drive(speed, steering_angle)

        # Publier des markers
        self.publish_markers(scan, best_gap, target_idx)

    def publish_drive(self, speed, steering_angle):
        msg = AckermannDriveStamped()
        msg.drive.speed = float(speed)
        msg.drive.steering_angle = float(steering_angle)
        self.drive_pub.publish(msg)

    def publish_markers(self, scan, gap, target_idx):
        # Marker du gap (ligne verte)
        gap_marker = Marker()
        gap_marker.header.frame_id = scan.header.frame_id
        gap_marker.type = Marker.LINE_STRIP
        gap_marker.action = Marker.ADD
        gap_marker.scale.x = 0.05
        gap_marker.color.g = 1.0
        gap_marker.color.a = 1.0

        for i in range(gap[0], gap[1]+1):
            angle = scan.angle_min + i * scan.angle_increment
            r = scan.ranges[i]
            x = r * np.cos(angle)
            y = r * np.sin(angle)
            gap_marker.points.append(Point(x=x, y=y, z=0.0))

        # Marker de la cible (sphere rouge)
        target_marker = Marker()
        target_marker.header.frame_id = scan.header.frame_id
        target_marker.type = Marker.SPHERE
        target_marker.action = Marker.ADD
        target_marker.scale.x = 0.2
        target_marker.scale.y = 0.2
        target_marker.scale.z = 0.2
        target_marker.color.r = 1.0
        target_marker.color.a = 1.0

        r = scan.ranges[target_idx]
        angle = scan.angle_min + target_idx * scan.angle_increment
        target_marker.pose.position.x = r * np.cos(angle)
        target_marker.pose.position.y = r * np.sin(angle)
        target_marker.pose.position.z = 0.0

        self.marker_pub.publish(gap_marker)
        self.marker_pub.publish(target_marker)


def main(args=None):
    rclpy.init(args=args)
    node = FollowTheGap()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
