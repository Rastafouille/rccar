from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration
from launch.actions import DeclareLaunchArgument
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():


    pkg_share = get_package_share_directory('rccar')
    config_dir = os.path.join(pkg_share, 'config')
    slam_toolbox_config = os.path.join(config_dir, 'slam_toolbox.yaml')

    return LaunchDescription([



        Node(
            package='slam_toolbox',
            executable='async_slam_toolbox_node',
            name='slam_toolbox',
            output='screen',
            parameters=[
                slam_toolbox_config]
                      )
    ])