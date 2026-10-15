import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, SetEnvironmentVariable
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    return LaunchDescription([
        SetEnvironmentVariable('ROS_LOCALHOST_ONLY','1'),
        SetEnvironmentVariable('ROS_DOMAIN_ID',os.environ.get('ROS_DOMAIN_ID','71')),
        DeclareLaunchArgument('port',default_value='8877'),
        DeclareLaunchArgument('autoplay',default_value='true'),
        DeclareLaunchArgument('public_playback',default_value='true'),
        DeclareLaunchArgument('rviz',default_value='false'),
        Node(package='cypher_robot_mind',executable='chess_lab',namespace='rolling_chess',
             parameters=[{'port':ParameterValue(LaunchConfiguration('port'),value_type=int),
                          'autoplay':ParameterValue(LaunchConfiguration('autoplay'),value_type=bool),
                          'public_playback':ParameterValue(LaunchConfiguration('public_playback'),value_type=bool)}],output='screen'),
        Node(package='rviz2',executable='rviz2',
             arguments=['-d',PathJoinSubstitution([FindPackageShare('cypher_robot_mind'),'config','chess.rviz'])],
             condition=IfCondition(LaunchConfiguration('rviz')))])
