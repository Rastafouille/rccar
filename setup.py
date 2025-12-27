from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'rccar'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*')),
        (os.path.join('share', package_name, 'description'), glob('description/*.xacro')),

    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='jerem',
    maintainer_email='you@example.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'autogap = rccar.autogap:main',
            'autogap_simu = rccar.autogap_simu:main',

            'rviz_overlay = rccar.rviz_overlay_node:main',
            'ftg_node = rccar.ftg_node:main',   
            'odom_simu_publisher = rccar.odom_simu_publisher:main',
            'e_stop_node = rccar.e_stop_node:main',


        ],
    },
)
