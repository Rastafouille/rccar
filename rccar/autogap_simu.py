#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rclpy
from rclpy.node import Node
import numpy as np
import math

from geometry_msgs.msg import Twist, Point32, Point
from visualization_msgs.msg import Marker
from sensor_msgs.msg import LaserScan, PointCloud
from ackermann_msgs.msg import AckermannDriveStamped

#from pynput import keyboard
from rclpy.time import Time
from rclpy.duration import Duration
from tf2_ros import TransformListener, Buffer
from rclpy.qos import QoSProfile, QoSReliabilityPolicy


class AutoGap(Node):
    def __init__(self):
        super().__init__('Autorace')

        # Paramètres
        self.declare_parameters(
            namespace='',
            parameters=[
                ('max_speed', 0.5), # m/s
                ('max_steer', 0.36), # rad (20°)
                ('angle_coef', 1.0), # coefficient pour l'angle de braquage
                ('range_angle', math.radians(160)), # champ de vision en rad
                ('dist_critique', 2.0), # distance en dessous de laquelle on réduit la vitesse
                ('dist_secu', 0.3), # distance de sécurité latérale pour obstacle proche
                ('angle_decalage', math.radians(35)), # angle de décalage pour obstacle proche
                ('angle_decalage_delta', math.radians(15)), # angle de décalage qui augmente avec la proximité
                ('distance_obst', 3.0), # distance en dessous de laquelle un obstacle est considéré proche
                ('range_angle_obst', math.radians(180)),    # champ de vision pour obstacle proche
            ]
        )

        # Charger les paramètres
        self.MAX_SPEED = self.get_parameter('max_speed').value
        self.MAX_STEER = self.get_parameter('max_steer').value
        self.ANGLE_COEF = self.get_parameter('angle_coef').value
        self.RANGE_ANGLE = self.get_parameter('range_angle').value
        self.DIST_CRITIQUE = self.get_parameter('dist_critique').value
        self.DIST_SECU = self.get_parameter('dist_secu').value
        self.ANGLE_DECALAGE = self.get_parameter('angle_decalage').value
        self.ANGLE_DECALAGE_DELTA = self.get_parameter('angle_decalage_delta').value
        self.DISTANCE_OBST = self.get_parameter('distance_obst').value
        self.RANGE_ANGLE_OBST = self.get_parameter('range_angle_obst').value

        # Variables
        self.RANGE_ID = 0
        self.ID_DECALAGE = 0
        self.ID_DECALAGE_DELTA = 0
        self.RANGE_ID_OBST = 0
        self.ranges = []
        self.angle_increment = 0.0
        self.angle_min = 0.0
        self.is_moving = True

        # Publishers
        self.pcl_pub = self.create_publisher(PointCloud, '/traj', 1)
        self.marker_cible_pub = self.create_publisher(Marker, '/cible_marker', 1)
        self.marker_loin_pub = self.create_publisher(Marker, '/loin_marker', 1)
        self.marker_collision_pub = self.create_publisher(Marker, '/collision_marker', 1)
        self.marker_zero_pub = self.create_publisher(Marker, '/zero_marker', 1)
        self.marker_cone_pub = self.create_publisher(Marker, '/cone_marker', 1)
        self.drive_pub = self.create_publisher(AckermannDriveStamped, '/drive', 1)

        # Messages init
        self.pcl_msg = PointCloud()
        self.pcl_msg.header.frame_id = "map"
        #self.pcl_msg.header.frame_id = "odom"


        self.marker_cible = self.create_marker("ego_racecar/laser", 2, 0, [1.0, 0.0, 0.0])
        self.marker_loin = self.create_marker("ego_racecar/laser", 2, 1, [0.0, 1.0, 0.0])
        self.marker_collision = self.create_marker("ego_racecar/laser", 2, 2, [0.0, 0.0, 1.0])
        self.marker_zero = self.create_marker("ego_racecar/laser", 2, 3, [1.0, 0.0, 1.0])

        #self.marker_cible = self.create_marker("laser", 2, 0, [1.0, 0.0, 0.0])
        #self.marker_loin = self.create_marker("laser", 2, 1, [0.0, 1.0, 0.0])
        #self.marker_collision = self.create_marker("laser", 2, 2, [0.0, 0.0, 1.0])
        #self.marker_zero = self.create_marker("laser", 2, 3, [1.0, 0.0, 1.0])

        
        # QoS pour Lidar
        qos_profile = QoSProfile(
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            depth=1
        )
        self.create_subscription(LaserScan, '/scan', self.laser_scan_callback, qos_profile)

        # Timer pour trajectoire
        self.timer = self.create_timer(0.1, self.add_point_traj)

        # Keyboard
        #self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press)
        #self.keyboard_listener.start()

        # TF
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        self.get_logger().info("AutoGap initialisé (fixed_frame = odom)")

    # def on_key_press(self, key):
    #     try:
    #         if key == keyboard.Key.space:
    #             self.is_moving = not self.is_moving
    #             status = "moving" if self.is_moving else "stopped"
    #             self.get_logger().info(f"SPACE pressed: {status}")
    #             if not self.is_moving:
    #                 stop = AckermannDriveStamped()
    #                 stop.drive.steering_angle = 0.0
    #                 stop.drive.speed = 0.0
    #                 self.drive_pub.publish(stop)
    #     except Exception as e:
    #         self.get_logger().error(f"Key press error: {e}") 

    def create_marker(self, frame_id, marker_type, marker_id, color):
            marker = Marker()
            marker.header.frame_id = frame_id
            marker.type = marker_type
            marker.id = marker_id
            marker.scale.x = 0.4
            marker.scale.y = 0.4
            marker.scale.z = 0.4
            marker.color.r, marker.color.g, marker.color.b = color
            marker.color.a = 1.0
            return marker

    def add_point_traj(self):
        try:
            # Récupérer la TF map -> base_link
            tf = self.tf_buffer.lookup_transform(
                'map', 'ego_racecar/base_link',
                Time(), timeout=Duration(seconds=0.05)
            )
            t = tf.transform.translation

            # Mise à jour de l’en-tête
            self.pcl_msg.header.stamp = self.get_clock().now().to_msg()

            # Ajouter le point courant
            p = Point32(x=t.x, y=t.y, z=t.z)
            self.pcl_msg.points.append(p)

            # Limiter le nombre de points pour éviter de surcharger RViz
            if len(self.pcl_msg.points) > 200:
                self.pcl_msg.points.pop(0)

            # Publier
            self.pcl_pub.publish(self.pcl_msg)

        except Exception as e:
            self.get_logger().warn(f"TF lookup failed: {e}")

    def laser_scan_callback(self, data):
        self.ranges = [0 if (math.isnan(r) or math.isinf(r)) else r for r in data.ranges]
        self.stamp = data.header.stamp
        self.angle_increment = data.angle_increment
        self.angle_min = data.angle_min
        self.half_len = len(self.ranges) // 2
        self.RANGE_ID = round(self.RANGE_ANGLE / self.angle_increment)
        self.ID_DECALAGE = round(self.ANGLE_DECALAGE / self.angle_increment)
        self.ID_DECALAGE_DELTA = round(self.ANGLE_DECALAGE_DELTA / self.angle_increment)
        self.RANGE_ID_OBST = round(self.RANGE_ANGLE_OBST / self.angle_increment)



            # Marker zéro
        #self.marker_zero.header.stamp = self.stamp
        #self.marker_zero.pose.position.x = self.ranges[self.half_len]
        #self.marker_zero.pose.position.y = 0.0
        #self.marker_zero_pub.publish(self.marker_zero)
        #print("marker_zero", self.marker_zero.pose.position.x, self.marker_zero.pose.position.y)
        self.process_scan()

    def process_scan(self):
        if not self.ranges:
            return

        start = max(0, self.half_len  - self.RANGE_ID // 2)
        stop = min(len(self.ranges), self.half_len + self.RANGE_ID // 2)

        local = self.ranges[start:stop]
        if len(local) == 0:
            return  # sécurité

        max_id = int(np.argmax(local)) + start
        max_range = self.ranges[max_id]
        max_angle = self.angle_min + max_id * self.angle_increment

        # Conversion polaire -> cartésien
        x = max_range * math.cos(max_angle)
        y = max_range * math.sin(max_angle)

        # ------------------------------
        # Marker ROS pour visualisation dans RViz
        # ------------------------------

        self.marker_loin.header.stamp = self.stamp
        self.marker_loin.pose.position.x = float(x)
        self.marker_loin.pose.position.y = float(y)
        self.marker_loin_pub.publish(self.marker_loin)

        # Log console
        #self.get_logger().info(f"Max point id={max_id}, r={max_range:.2f}, angle={math.degrees(max_angle):.1f}°, " f"x={x:.2f}, y={y:.2f}" )



        # Vérifier obstacles proches dans cône
        obst_id, mini = 0, 1e9
        for i in range(max_id - self.RANGE_ID_OBST//2, max_id + self.RANGE_ID_OBST//2):
            if 0 <= i < len(self.ranges):
                r = self.ranges[i]
                if 0 < r < self.DISTANCE_OBST:
                    lat = math.sin((i - max_id) * self.angle_increment) * r
                    if abs(lat) < self.DIST_SECU and r < mini:
                        obst_id, mini = i, r

        self.marker_collision.header.stamp = self.stamp
        if obst_id:
            col_angle = self.angle_min + obst_id * self.angle_increment
            self.marker_collision.pose.position.x = self.ranges[obst_id] * math.cos(col_angle)
            self.marker_collision.pose.position.y = self.ranges[obst_id] * math.sin(col_angle)
            self.marker_collision_pub.publish(self.marker_collision)

            delta = int(self.ID_DECALAGE - self.ranges[obst_id] * self.ID_DECALAGE_DELTA)
            if obst_id > max_id:
                max_id -= delta
            else:
                max_id += delta
            max_id = max(0, min(len(self.ranges)-1, max_id))
            max_range = self.ranges[max_id]
            max_angle = self.angle_min + max_id * self.angle_increment
        else:
            self.marker_collision.pose.position.x = 1000.0
            self.marker_collision.pose.position.y = 1000.0
            self.marker_collision_pub.publish(self.marker_collision)

        # Marker cible
        self.marker_cible.header.stamp = self.stamp
        self.marker_cible.pose.position.x = max_range * math.cos(max_angle)
        self.marker_cible.pose.position.y = max_range * math.sin(max_angle)
        self.marker_cible_pub.publish(self.marker_cible)

        # Commande
        if not self.is_moving or max_range <= 0.0:
            self.get_logger().info("PRESS SPACE TO START !!")
            return

        drive = AckermannDriveStamped()
        steer = math.atan2(math.sin(max_angle), math.cos(max_angle)) * self.ANGLE_COEF
        drive.drive.steering_angle = np.clip(steer, -self.MAX_STEER, self.MAX_STEER)
        drive.drive.speed = self.calculate_speed(max_angle, max_range)
        self.drive_pub.publish(drive)

    def calculate_speed(self, angle, distance):
        if distance >= self.DIST_CRITIQUE:
            return self.MAX_SPEED
        else:
            return self.MAX_SPEED * (distance / self.DIST_CRITIQUE)


def main(args=None):
    rclpy.init(args=args)
    node = AutoGap()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
