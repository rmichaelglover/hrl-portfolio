from glob import glob
from setuptools import setup

setup(
    name='cypher_robot_mind', version='0.2.0', packages=['cypher_robot_mind'],
    data_files=[('share/ament_index/resource_index/packages', ['resource/cypher_robot_mind']),
                ('share/cypher_robot_mind', ['package.xml', 'README.md', 'CHESS_PHYSICS.md', 'LICENSE']),
                ('share/cypher_robot_mind/launch', glob('launch/*.py')),
                ('share/cypher_robot_mind/config', glob('config/*')),
                ('share/cypher_robot_mind/web', glob('web/*'))],
    install_requires=['setuptools', 'numpy'], zip_safe=True,
    maintainer='R. Michael Glover', maintainer_email='rmichaelglover@users.noreply.github.com',
    description='Virtual embodied HRL robot mind for ROS 2 Humble', license='MIRL-1.0',
    entry_points={'console_scripts': [
        'chess_lab = cypher_robot_mind.chess_lab_node:main',
        'world = cypher_robot_mind.world_node:main',
        'mind = cypher_robot_mind.mind_node:main',
        'view = cypher_robot_mind.view_node:main',
        'dashboard = cypher_robot_mind.dashboard_node:main']})
