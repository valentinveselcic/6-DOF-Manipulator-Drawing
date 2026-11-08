from setuptools import find_packages, setup

package_name = 'draw_task'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='student',
    maintainer_email='student@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [ "test_pymoveit2 = draw_task.test_pymoveit2:main"
                            ,"robot_drawer = draw_task.robot_drawer:main"
                            ,"path_visualizer = draw_task.path_visualizer:main"
        ],
    },
)
