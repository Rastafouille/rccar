from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    pkg_share = get_package_share_directory('rccar')
    config_dir = os.path.join(pkg_share, 'config')
    cartographer_config = os.path.join(config_dir, 'cartographer.lua')

    return LaunchDescription([
        Node(
            package='cartographer_ros',
            executable='cartographer_node',
            name='cartographer_node',
            output='screen',
            arguments=['-configuration_directory', config_dir,
                       '-configuration_basename', 'cartographer.lua'],
            remappings=[
                ('scan', '/scan'),
                ('odom', '/odom')
            ]
        ),
        Node(
            package='cartographer_ros',
            executable='cartographer_occupancy_grid_node',
            name='occupancy_grid_node',
            output='screen',
            arguments=['-resolution', '0.05', '-publish_period_sec', '1.0']
        )
    ])
