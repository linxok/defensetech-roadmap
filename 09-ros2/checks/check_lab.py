#!/usr/bin/env python3
"""Перевірка лабораторної 09: ROS2 Telemetry Bridge.

ROS2 у CI немає, тому перевіряється чиста логіка `bridge_logic.py`
(без імпорту rclpy) та структура вузла `telemetry_bridge.py`.

Запуск:
    python checks/check_lab.py --target solution
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODULE = HERE.parent


def fail(message: str) -> None:
    print(f'FAIL: {message}')
    raise SystemExit(1)


def load_logic(target: Path):
    path = target / 'bridge_logic.py'
    if not path.is_file():
        fail(f'{path} не існує (конвертація має жити поза rclpy)')
    spec = importlib.util.spec_from_file_location('student_bridge_logic', path)
    module = importlib.util.module_from_spec(spec)
    sys.modules['student_bridge_logic'] = module
    try:
        spec.loader.exec_module(module)
    except Exception as exc:  # noqa: BLE001
        fail(f'bridge_logic не імпортується без ROS2: {exc!r}')
    if not hasattr(module, 'mavlink_to_dict'):
        fail('у bridge_logic немає `mavlink_to_dict`')
    return module


class FakeMessage:
    def __init__(self, kind: str, system_id: int = 7, **fields) -> None:
        self._kind = kind
        self._system_id = system_id
        for key, value in fields.items():
            setattr(self, key, value)

    def get_type(self) -> str:
        return self._kind

    def get_srcSystem(self) -> int:
        return self._system_id


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', type=Path, default=MODULE / 'solution')
    args = parser.parse_args()

    module = load_logic(args.target)

    position = FakeMessage(
        'GLOBAL_POSITION_INT', lat=504501000, lon=305234000, alt=120000, hdg=9000
    )
    payload = module.mavlink_to_dict(position)
    if not payload or abs(payload['lat'] - 50.4501) > 1e-4:
        fail(f'невірна конвертація GLOBAL_POSITION_INT: {payload}')

    battery = FakeMessage('BATTERY_STATUS', battery_remaining=87)
    if module.mavlink_to_dict(battery)['battery'] != 87:
        fail('невірна конвертація BATTERY_STATUS')

    if module.mavlink_to_dict(FakeMessage('HEARTBEAT')) is not None:
        fail('HEARTBEAT не має потрапляти в топік')

    node_path = args.target / 'telemetry_bridge.py'
    if not node_path.is_file():
        fail('немає `telemetry_bridge.py`')
    source = node_path.read_text(encoding='utf-8')
    for pattern in ('create_publisher', 'drone/telemetry', 'destroy_node', 'rclpy.spin'):
        if pattern not in source:
            fail(f'у вузлі немає `{pattern}`')

    print('PASS: конвертація тестується без ROS2, вузол має потрібну структуру')
    return 0


if __name__ == '__main__':
    sys.exit(main())
