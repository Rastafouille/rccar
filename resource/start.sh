#!/bin/bash

############################
# Screen 1 : teleop
############################
screen -dmS rccar_teleop bash -c "
# attendre que le joystick apparaisse
sleep 30
source /opt/ros/humble/setup.bash
source ~/rccar_ws/install/setup.bash
export ROS_DOMAIN_ID=111
ros2 launch rccar teleop.launch.py
exec bash
"

############################
# Screen 2 : bringup
############################
screen -dmS rccar_bringup bash -c "
source /opt/ros/humble/setup.bash
source ~/rccar_ws/install/setup.bash
export ROS_DOMAIN_ID=111
ros2 launch rccar bringup_launch.py
exec bash
"

############################
# Screen 3 : stream video
############################
screen -dmS rccar_stream bash -c "

# environnement Python (si nécessaire)
# source ~/venv/bin/activate

python3 /home/aresuser/rccar_ws/src/rccar/resource/stream.py
exec bash
"

