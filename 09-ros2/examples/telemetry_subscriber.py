import rclpy
from std_msgs.msg import String

def callback(msg):
    print(f'Received: {msg.data}')

rclpy.init()
node = rclpy.create_node('telemetry_subscriber')
sub = node.create_subscription(String, 'drone/telemetry', callback, 10)
rclpy.spin(node)
