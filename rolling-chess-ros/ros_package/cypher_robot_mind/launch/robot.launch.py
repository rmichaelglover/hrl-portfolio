from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, SetEnvironmentVariable
import secrets
import os
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    namespace='cypher'
    nodes=[Node(package='cypher_robot_mind',executable=exe,namespace=namespace,output='screen')
           for exe in ['world','mind','view']]
    nodes.append(Node(package='cypher_robot_mind',executable='dashboard',namespace=namespace,
                      parameters=[{'port':LaunchConfiguration('port')}],output='screen'))
    nodes.append(Node(package='rviz2',executable='rviz2',
                      arguments=['-d',PathJoinSubstitution([FindPackageShare('cypher_robot_mind'),'config','mind.rviz'])],
                      condition=IfCondition(LaunchConfiguration('rviz'))))
    return LaunchDescription([SetEnvironmentVariable('ROS_LOCALHOST_ONLY','1'),
                              SetEnvironmentVariable('ROS_DOMAIN_ID',os.environ.get('ROS_DOMAIN_ID','71')),
                              SetEnvironmentVariable('CYPHER_COMMAND_SECRET',secrets.token_hex(32)),
                              DeclareLaunchArgument('rviz',default_value='false'),
                              DeclareLaunchArgument('port',default_value='8876')]+nodes)
