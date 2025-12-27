import os
import launch
import launch_ros.actions
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    # Définition de l'argument "map"
    map_arg = DeclareLaunchArgument(
        'map',
        default_value='lnpa',
        description='Nom de la carte utilisée'
    )

    # Utilisation de `LaunchConfiguration` pour le paramètre map
    config_file = os.path.join(
        get_package_share_directory('rccar'),
        'config',
        'autogap_' + LaunchConfiguration('map').perform({})
    )

    return LaunchDescription([
        map_arg,

        # AutoGap Node
        launch_ros.actions.Node(
            package='rccar',
            executable='autogap',
            name='autogap_node',
            output='screen',
            parameters=[config_file]
        ),

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
