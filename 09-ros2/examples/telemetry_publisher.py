import json

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class TelemetryPublisher(Node):
    def __init__(self) -> None:
        super().__init__('telemetry_publisher')
        self.publisher = self.create_publisher(String, 'drone/telemetry', 10)
        self.create_timer(0.1, self.publish)

    def publish(self) -> None:
        msg = String()
        msg.data = json.dumps({'alt': 100.0, 'battery': 87, 'heading': 90.0})
        self.publisher.publish(msg)


def main() -> None:
    rclpy.init()
    node = TelemetryPublisher()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
