sudo apt update
sudo apt install mesa-utils

export __NV_PRIME_RENDER_OFFLOAD=1 && export __GLX_VENDOR_LIBRARY_NAME=nvidia && export __VK_LAYER_NV_optimus=NVIDIA_only && export LIBGL_ALWAYS_INDIRECT=1

glxinfo | grep OpenGL

source /opt/ros/foxy/setup.bash
source /sim_ws/install/local_setup.bash
export ROS_DOMAIN_ID=1

#ros2 launch f1tenth_gym_ros gym_bridge_launch.py
