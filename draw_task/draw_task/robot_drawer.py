#!/usr/bin/env python3

from threading import Thread
import math
import rclpy
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.node import Node
from std_msgs.msg import Bool
from tf_transformations import quaternion_from_euler
from pymoveit2 import MoveIt2

class RobotDrawer(Node):
    def __init__(self):
        super().__init__('robot_drawer')
        
        self.draw_pub = self.create_publisher(Bool, '/draw_enable', 10)
        
        callback_group = ReentrantCallbackGroup()
        
        # MoveIt2 interface
        self.moveit2 = MoveIt2(
            node=self,
            joint_names=['joint_1', 'joint_2', 'joint_3', 'joint_4', 'joint_5', 'joint_6'],
            base_link_name='base_link',
            end_effector_name='link_6',
            group_name='arm',
            callback_group=callback_group
        )
        
        self.moveit2.planner_id = "RRTConnectkConfigDefault"
        
        self.moveit2.max_velocity = 0.5
        self.moveit2.max_acceleration = 0.5
        
        self.get_logger().info('Robot Drawer node started')
    
    def enable_drawing(self, enable):
        """Omogući/onemogući crtanje"""
        msg = Bool()
        msg.data = enable
        self.draw_pub.publish(msg)
        self.get_logger().info(f'Drawing {"enabled" if enable else "disabled"}')
    
    def move_to_position(self, x, y, z, roll=0.0, pitch=3.14/2, yaw=0.0):
        """Pomakni end effector na zadanu poziciju"""
        q = quaternion_from_euler(roll, pitch, yaw)
        quat_xyzw = [q[0], q[1], q[2], q[3]]
        
        self.get_logger().info(f'Moving to position: [{x:.3f}, {y:.3f}, {z:.3f}]')

        cartesian = False
        cartesian_max_step = 0.0025
        cartesian_fraction_threshold = 0.0
        cartesian_jump_threshold = 0.0
        cartesian_avoid_collisions = False
        # Set parameters for cartesian planning
        self.moveit2.cartesian_avoid_collisions = cartesian_avoid_collisions
        self.moveit2.cartesian_jump_threshold = cartesian_jump_threshold

        self.moveit2.move_to_pose(
            position=[x, y, z],
            quat_xyzw=quat_xyzw,
            cartesian=cartesian,
            cartesian_max_step=cartesian_max_step,
            cartesian_fraction_threshold=cartesian_fraction_threshold   
        )
        
        self.moveit2.wait_until_executed()
        return (x, y, z)
    
    def draw_name(self, start_x=1.0, start_y=-0.75, start_z=2.0):
        """Nacrtaj slovo L"""
        self.get_logger().info('Drawing name')
        
        # Idi na početnu poziciju (bez crtanja)
        self.enable_drawing(False)
        self.move_to_position(start_x, start_y, start_z)
        
        
        self.enable_drawing(True)
        # L
        x,y,z = self.move_to_position(start_x, start_y, start_z - 0.5)
        x,y,z = self.move_to_position(x, y + 0.25, z)

        self.enable_drawing(False)       
        # E
        x,y,z = self.move_to_position(x, y + 0.3, z)
        self.enable_drawing(True)
        x,y,z = self.move_to_position(x, y + 0.25, z)
        x,y,z = self.move_to_position(x, y - 0.25, z)
        x,y,z = self.move_to_position(x, y, z + 0.25)
        x,y,z = self.move_to_position(x, y + 0.25, z)
        x,y,z = self.move_to_position(x, y - 0.25, z)
        x,y,z = self.move_to_position(x, y, z + 0.25)
        x,y,z = self.move_to_position(x, y + 0.25, z)
        x,y,z = self.move_to_position(x, y - 0.25, z)

        self.enable_drawing(False)
        # N
        x,y,z = self.move_to_position(x, y + 0.55, z - 0.5)
        self.enable_drawing(True)
        x,y,z = self.move_to_position(x, y, z + 0.5)
        x,y,z = self.move_to_position(x, y + 0.3, z - 0.5)
        x,y,z = self.move_to_position(x, y, z+0.5)
        
        self.enable_drawing(False)
    
    def go_home(self):
        """Vrati robot u home poziciju"""
        self.get_logger().info('Going to home position')
        
        home_joints = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.moveit2.move_to_configuration(home_joints)
        self.moveit2.wait_until_executed()
        
        self.get_logger().info('Home position reached')


def main(args=None):
    rclpy.init(args=args)
    
    node = RobotDrawer()
    
    executor = rclpy.executors.MultiThreadedExecutor(2)
    executor.add_node(node)
    executor_thread = Thread(target=executor.spin, daemon=True)
    executor_thread.start()
    
    node.get_clock().sleep_for(rclpy.duration.Duration(seconds=2))
    
    try:
        node.draw_name()
        
        node.go_home()
        
    except KeyboardInterrupt:
        pass
    
    rclpy.shutdown()
    executor_thread.join()


if __name__ == '__main__':
    main()
