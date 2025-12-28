# RCCAR ROS2

## Ma config
Base voiture Absima AB3.4
Batterie 3S
Moteur Rush stock SE 17.5T TETC (nbre de poles=4)
Diametre roue en charge environ 84mm
Pignon 19 couronne 83 --> ratio 4.37
Reduction interne de ce modèle 2.6
speed_to_erpm_gain = (60*2.6*4.37*4)/(pi*0.084)=10 370


## réseau
jetson  en hotspot RCCAR, adresse 192.168.42.1 (pour eviter les conflits avec le Hokuyo)

## Simulation

pour la simulation f1tenth ros2 : <https://github.com/f1tenth/f1tenth_gym_ros>

'ros2 launch f1tenth_gym_ros gym_bridge_launch.py'

en teleop 
'ros2 launch rccar teleop.launch.py'

en autonome
'ros2 launch rccar autogap_simu.launch.py' 



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


### f1tenth stack
https://roboracer.ai/build.html
https://github.com/f1tenth/f1tenth_system/tree/humble-devel

il y a des modif a faire des les appel de parametres
    speed_to_erpm_gain_ = declare_parameter<double>("speed_to_erpm_gain", 1.0);

un soucis de version de setuptools
pip install setuptools==65.0.0 fonctionne

des - a remplacer par des _ dans les fichierssetup.cfg

utiliser les fichiers de config et launch dans le package rccar data/f1tenth_system/f1tenth_stack/config et launch

https://github.com/f1tenth/f1tenth_system/tree/humble-devel 
avec les fichiers de config et launch dans resource/f1tenth_system/f1tenth_stack/config et launch

'ros2 launch rccar bringup_launch.py'

### au demarrage

je lance le bringup + teleop + stream webcam depuis un script start.sh avec crontab
ca initialise 3 screen
la camera est streamer avec opencv, sur http://10.42.0.1:8080




