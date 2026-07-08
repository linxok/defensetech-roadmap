import rclpy
from std_msgs.msg import String

rclpy.init()
node = rclpy.create_node('telemetry_publisher')
publisher = node.create_publisher(String, 'drone/telemetry', 10)

msg = String()
msg.data = '{"alt": 100, "battery": 87}'
publisher.publish(msg)
print('Published telemetry')
