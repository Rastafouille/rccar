#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import math

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSReliabilityPolicy

from sensor_msgs.msg import LaserScan, Joy
from std_msgs.msg import Bool
from ackermann_msgs.msg import AckermannDriveStamped


class EStopNode(Node):

    def __init__(self):
        super().__init__('e_stop_node')

        # ---------- PARAMS ----------
        self.declare_parameter('stop_distance', 0.15)     # meters
        self.declare_parameter('front_angle_deg', 15.0)   # +/- degrees
        self.declare_parameter('r1_button_index', 5)

        self.stop_distance = self.get_parameter('stop_distance').value
        self.front_angle = math.radians(
            self.get_parameter('front_angle_deg').value
        )
        self.r1_index = self.get_parameter('r1_button_index').value

        # ---------- STATE ----------
        self.front_min_dist = float('inf')
        self.r1_pressed = False
        self.estop_active = False

        # ---------- QoS (LOW LATENCY) ----------
        qos = QoSProfile(
            depth=1,
            reliability=QoSReliabilityPolicy.BEST_EFFORT
        )

        # ---------- SUBSCRIBERS ----------
        self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            qos
        )

        self.create_subscription(
            Joy,
            '/joy',
            self.joy_callback,
            qos
        )

        # ---------- PUBLISHERS ----------
        self.estop_pub = self.create_publisher(
            Bool,
            '/e_stop',
            qos
        )

        self.emergency_drive_pub = self.create_publisher(
            AckermannDriveStamped,
            '/emergency_drive',
            qos
        )

        # Timer @ 50 Hz
        self.create_timer(0.02, self.timer_callback)

        self.get_logger().info('🚨 E-STOP node started')

    # --------------------------------------------------

    def scan_callback(self, msg: LaserScan):
        """Compute min distance in front cone"""
        min_dist = float('inf')

        angle = msg.angle_min
        for r in msg.ranges:
            if abs(angle) <= self.front_angle:
                if msg.range_min < r < msg.range_max:
                    min_dist = min(min_dist, r)
            angle += msg.angle_increment

        self.front_min_dist = min_dist

    # --------------------------------------------------

    def joy_callback(self, msg: Joy):
        if len(msg.buttons) > self.r1_index:
            self.r1_pressed = msg.buttons[self.r1_index] == 1
        else:
            self.r1_pressed = False

    # --------------------------------------------------

    def timer_callback(self):
        obstacle = self.front_min_dist < self.stop_distance
        self.estop_active = obstacle or self.r1_pressed

        # Publish e-stop state
        estop_msg = Bool()
        estop_msg.data = self.estop_active
        self.estop_pub.publish(estop_msg)

        # If e-stop active → force STOP command
        if self.estop_active:
            stop_msg = AckermannDriveStamped()
            stop_msg.header.stamp = self.get_clock().now().to_msg()
            stop_msg.drive.speed = 0.0
            stop_msg.drive.steering_angle = 0.0
            stop_msg.drive.acceleration = 0.0
            self.emergency_drive_pub.publish(stop_msg)


def main(args=None):
    rclpy.init(args=args)
    node = EStopNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
