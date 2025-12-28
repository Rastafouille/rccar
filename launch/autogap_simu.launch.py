from launch import LaunchDescription
from launch.substitutions import  PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
 
    config_file = PathJoinSubstitution([
        FindPackageShare('rccar'),
        'config',
        'autogap_TRR.yaml'
    ])

    return LaunchDescription([

        Node(
            package='rccar',
            executable='autogap_simu',
            name='autogap_simu_node',
            output='screen',
            parameters=[config_file]
        )


        # RVIZ Overlay (désactivé)
        # launch_ros.actions.Node(
        #     package='rccar',
        #     executable='rviz_overlay_simu',
        #     name='rviz_overlay_node',
        #     output='screen'
        # ),

        # Détection de collision (désactivée)
        # launch_ros.actions.Node(
        #     package='rccar',
        #     executable='detection_collision',
        #     name='collision_detection_node',
        #     output='screen'
        # ),

        # Chronométrage des tours (laps) (désactivé)
        # launch_ros.actions.Node(
        #     package='rccar',
        #     executable='lap_timer',
        #     name='laps_node',
        #     output='screen'
        # ),
    ])
