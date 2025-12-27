# RCCAR ROS2


## réseau
Pc portable en hotspot jerem-Precision-7760, adresse 192.168.10.1
Jetson adresse 192.168.10.222


## Simulation

pour la simulation f1tenth ros2 : <https://github.com/f1tenth/f1tenth_gym_ros>

'ros2 launch f1tenth_gym_ros gym_bridge_launch.py'



## VESC 
package : <https://github.com/f1tenth/vesc>


## config

pour le teleop tool
https://github.com/ros-teleop/teleop_tools.git


# coté voiture

### pour le parametrage reseau hokuyo

Activer NetworkManager pour gérer la connexion
Si vous préférez utiliser NetworkManager, assurez-vous qu'il est actif et configuré pour gérer eth0.

Activez NetworkManager :

"sudo systemctl enable NetworkManager"
"sudo systemctl start NetworkManager"

Configurez eth0 via nmcli :

"nmcli con add type ethernet con-name hokuyo ifname eth0 ip4 10.42.0.10/24 gw4 10.42.0.1"

Redémarrez le service :

"sudo systemctl restart NetworkManager"

package hokuyo : https://github.com/Hokuyo-aut/urg_node2 

### reseau wifi

parametrer un hotspot wifi "rccar" et le lancer au demarrage

### f1tenth stack
https://roboracer.ai/build.html
https://github.com/f1tenth/f1tenth_system/tree/humble-devel

il y a des modif a faire des les appel de paremtre
    speed_to_erpm_gain_ = declare_parameter<double>("speed_to_erpm_gain", 1.0);

un soucis de version de setuptools
pip install setuptools==65.0.0 fonctionne

des - a remplacer par des _ dans les fichierssetup.cfg

utiliser les fichiers de config et launch dans data/f1tenth_system/f1tenth_stack/config et launch

https://github.com/f1tenth/f1tenth_system/tree/humble-devel 
avec les fichiers de config et launch dans ressource/f1tenth_system/f1tenth_stack/config et launch

'ros2 launch rccar bringup_launch.py'

### au demarrage

je lance le bringup + teleop + stream webcam depuis un script start.sh avec crontab
ca initialise 3 screen
la camera est streamer avec opencv, sur http://10.42.0.1:8080




