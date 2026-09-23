import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class StatusPublisher(Node):
    def __init__(self) -> None:
        super().__init__('status_publisher')
        self.publisher = self.create_publisher(String, 'drone/status', 10)
        self.create_timer(1.0, self.publish)

    def publish(self) -> None:
        msg = String()
        msg.data = 'armed'
        self.publisher.publish(msg)


def main() -> None:
    rclpy.init()
    node = StatusPublisher()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
