"""ROS2-вузол: публікує телеметрію у топік `drone/telemetry`.

Запуск (після `colcon build`):

    ros2 run drone_bridge telemetry_bridge

Вузол навмисно розділений: уся конвертація — у `bridge_logic.py`
(тестується без ROS2), тут — лише інтеграція з rclpy.
"""

from __future__ import annotations

import json
from typing import Any

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

if __package__:
    from .bridge_logic import mavlink_to_dict
else:
    from bridge_logic import mavlink_to_dict


class TelemetryBridge(Node):
    def __init__(self) -> None:
        super().__init__('telemetry_bridge')
        self.publisher = self.create_publisher(String, 'drone/telemetry', 10)
        self.get_logger().info('telemetry bridge started on drone/telemetry')

    def publish_message(self, message: Any) -> bool:
        """Конвертує MAVLink-повідомлення та публікує його. False — пропуск."""
        payload = mavlink_to_dict(message)
        if payload is None:
            return False
        msg = String()
        msg.data = json.dumps(payload, ensure_ascii=False)
        self.publisher.publish(msg)
        return True


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = TelemetryBridge()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
