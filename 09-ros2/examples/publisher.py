import rclpy
from std_msgs.msg import String

rclpy.init()
node = rclpy.create_node('telemetry_publisher')
publisher = node.create_publisher(String, 'drone/status', 10)
msg = String()
msg.data = 'armed'
publisher.publish(msg)
print("Published drone/status")
