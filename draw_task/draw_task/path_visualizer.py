#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point
from visualization_msgs.msg import Marker, MarkerArray
from std_msgs.msg import Bool, ColorRGBA
import tf2_ros
from tf2_ros import TransformException


class PathVisualizer(Node):
    def __init__(self):
        super().__init__('path_visualizer')
        
        self.marker_pub = self.create_publisher(MarkerArray, '/robot_path', 10)
        
        self.draw_sub = self.create_subscription(
            Bool,
            '/draw_enable',
            self.draw_callback,
            10
        )
        
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)
        
        self.completed_segments = []
        
        self.current_segment = []
        
        self.is_drawing = False
        
        self.timer = self.create_timer(0.1, self.update_path)  
        
        self.get_logger().info('[Path Visualizer] Node started ==================================================')
    
    def draw_callback(self, msg):
        if self.is_drawing and not msg.data:
            if len(self.current_segment) > 1:
                self.completed_segments.append(self.current_segment[:])  
                self.current_segment = []  
        
        elif not self.is_drawing and msg.data:
            self.current_segment = []
        
        self.is_drawing = msg.data
    
    def update_path(self):
        
        if not self.is_drawing:
            return
        
        try:
            transform = self.tf_buffer.lookup_transform(
                'world',
                'link_6',
                rclpy.time.Time(),
                timeout=rclpy.duration.Duration(seconds=0.1)
            )
            
            point = Point()
            point.x = transform.transform.translation.x
            point.y = transform.transform.translation.y
            point.z = transform.transform.translation.z
            
            self.current_segment.append(point)
            
            self.publish_markers()
            
        except TransformException as ex:
            self.get_logger().warn(f'[Path Visualizer] Could not transform: {ex}')
    
    def publish_markers(self):
        marker_array = MarkerArray()
        
        for i, segment in enumerate(self.completed_segments):
            marker = self.create_line_marker(i, segment, completed=True)
            marker_array.markers.append(marker)
        
        if len(self.current_segment) > 0:
            marker = self.create_line_marker(
                len(self.completed_segments), 
                self.current_segment, 
                completed=False
            )
            marker_array.markers.append(marker)
        
        self.marker_pub.publish(marker_array)
    
    def create_line_marker(self, marker_id, points, completed=True):
        marker = Marker()
        marker.header.frame_id = 'world'
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.ns = 'robot_path'
        marker.id = marker_id
        marker.type = Marker.LINE_STRIP
        marker.action = Marker.ADD
        
        marker.pose.orientation.w = 1.0
        marker.scale.x = 0.005  
        
        marker.color = ColorRGBA()

        marker.color.r = 0.0
        marker.color.g = 1.0
        marker.color.b = 0.0
        marker.color.a = 1.0

        marker.points = points
        marker.lifetime.sec = 0
        
        return marker


def main(args=None):
    rclpy.init(args=args)
    node = PathVisualizer()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
