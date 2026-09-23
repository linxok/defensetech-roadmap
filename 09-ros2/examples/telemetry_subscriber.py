import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class TelemetrySubscriber(Node):
    def __init__(self) -> None:
        super().__init__('telemetry_subscriber')
        self.create_subscription(String, 'drone/telemetry', self.callback, 10)

    def callback(self, msg: String) -> None:
        print(f'Received: {msg.data}')


def main() -> None:
    rclpy.init()
    node = TelemetrySubscriber()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
