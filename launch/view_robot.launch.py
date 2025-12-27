from launch import LaunchDescription
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node
import os
import xacro

def generate_launch_description():


    pkg_share = get_package_share_directory('rccar')

    urdf_file = os.path.join(pkg_share, 'description', 'racecar.xacro')
    

    # Conversion Xacro → URDF
    robot_description_config = xacro.process_file(urdf_file).toxml()


    return LaunchDescription([
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{
                'use_sim_time': False,
                'robot_description': robot_description_config
            }],
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', os.path.join(pkg_share, 'config', 'robotrace.rviz')],
        )
    ])
