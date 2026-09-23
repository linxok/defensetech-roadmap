# Лабораторна робота 09: ROS2 Telemetry Bridge

## Мета

Створити ROS2-пакет `drone_bridge` з вузлом `telemetry_bridge.py`, який публікує
MAVLink-телеметрію у топік `drone/telemetry`, і чистою логікою конвертації
`bridge_logic.py`, яка тестується без встановленого ROS2.

## Передумови

- ROS2 Humble встановлено; у кожному терміналі: `source /opt/ros/humble/setup.bash`.
- Workspace `~/ros2_ws/src` створено.
- Репозиторій курсу доступний локально (для `checks/` і `solution/`).

## Контракт перевірки

`python 09-ros2/checks/check_lab.py --target <тека>` очікує теку, у якій
напряму лежать два файли:

| Файл | Що перевіряється |
|---|---|
| `bridge_logic.py` | імпортується без rclpy; є `mavlink_to_dict(message: Any) -> dict[str, Any] \| None` |
| `telemetry_bridge.py` | у тексті є `create_publisher`, `drone/telemetry`, `destroy_node`, `rclpy.spin` |

Конвертація використовує лише два методи вхідного повідомлення:
`message.get_type()` і `message.get_srcSystem()`. Поля `type` і `system_id`
додаються до кожного опублікованого словника.

| Вхід (FakeMessage у check) | Очікуваний результат |
|---|---|
| `GLOBAL_POSITION_INT(lat=504501000, lon=305234000, alt=120000, hdg=9000)` | `lat ≈ 50.4501`, `lon ≈ 30.5234`, `alt = 120.0`, `heading = 90.0` |
| `BATTERY_STATUS(battery_remaining=87)` | `battery = 87` |
| `HEARTBEAT` | `None` — у топік не публікується |

## Кроки

### 1. Створення пакета

```bash
source /opt/ros/humble/setup.bash
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_python drone_bridge --dependencies rclpy std_msgs
```

Структура пакета після цього кроку (теку `launch/` створіть вручну):

```text
~/ros2_ws/src/drone_bridge/
├── package.xml
├── setup.cfg
├── setup.py
├── resource/drone_bridge
├── launch/
│   └── bridge.launch.py
└── drone_bridge/
    ├── __init__.py
    ├── bridge_logic.py
    └── telemetry_bridge.py
```

Тека `drone_bridge/drone_bridge/` — саме той `<тека студента>`, яку отримує
`check_lab.py --target`.

### 2. `bridge_logic.py` — чиста логіка без rclpy

Створіть `drone_bridge/drone_bridge/bridge_logic.py` (звірте з
`09-ros2/solution/bridge_logic.py`):

```python
"""Чиста логіка ROS2-моста: MAVLink-повідомлення → dict (тестується без ROS2)."""

from __future__ import annotations

from typing import Any

TRACKED_TYPES = {'GLOBAL_POSITION_INT', 'BATTERY_STATUS', 'SYS_STATUS', 'VFR_HUD'}


def mavlink_to_dict(message: Any) -> dict[str, Any] | None:
    """Повертає словник телеметрії для публікації в ROS2-топік."""
    kind = message.get_type()
    if kind not in TRACKED_TYPES:
        return None

    payload: dict[str, Any] = {'type': kind, 'system_id': message.get_srcSystem()}
    if kind == 'GLOBAL_POSITION_INT':
        payload.update(
            lat=message.lat / 1e7,
            lon=message.lon / 1e7,
            alt=message.alt / 1000.0,
            heading=message.hdg / 100.0 if message.hdg != 65535 else None,
        )
    elif kind == 'BATTERY_STATUS':
        payload['battery'] = message.battery_remaining
    elif kind == 'SYS_STATUS':
        payload.update(
            battery=message.battery_remaining,
            voltage=message.voltage_battery / 1000.0,
        )
    elif kind == 'VFR_HUD':
        payload.update(
            airspeed=message.airspeed,
            groundspeed=message.groundspeed,
            alt=message.alt,
            climb=message.climb,
        )
    return payload
```

`TRACKED_TYPES` навмисно не містить `HEARTBEAT`: контракт вимагає повертати
`None`, тобто не публікувати цей тип.

### 3. `telemetry_bridge.py` — вузол

Створіть `drone_bridge/drone_bridge/telemetry_bridge.py` (звірте з
`09-ros2/solution/telemetry_bridge.py`):

```python
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
```

Ключові вимоги, які шукає `check_lab.py` у тексті вузла:

- `create_publisher` з топіком `'drone/telemetry'` і чергою `10`;
- `destroy_node` і `rclpy.shutdown` у `finally`;
- `rclpy.spin(node)` у `main`.

Імпорт `from .bridge_logic import mavlink_to_dict` працює, коли модуль
виконується всередині пакета (`ros2 run`); запасний `from bridge_logic import
mavlink_to_dict` — коли обидва файли лежать в одній теці (перевірка без пакета).

### 4. Launch-файл

Створіть `drone_bridge/launch/bridge.launch.py`:

```python
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='drone_bridge',
            executable='telemetry_bridge',
            name='telemetry_bridge',
            output='screen',
        ),
    ])
```

### 5. `setup.py` — entry point вузла

Замініть згенерований `setup.py` (файл `setup.cfg` з `ros2 pkg create` не
видаляйте):

```python
from glob import glob

from setuptools import find_packages, setup

package_name = 'drone_bridge'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='student',
    maintainer_email='student@example.com',
    description='ROS2 telemetry bridge',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'telemetry_bridge = drone_bridge.telemetry_bridge:main',
        ],
    },
)
```

### 6. Build і запуск

```bash
cd ~/ros2_ws
colcon build --packages-select drone_bridge
source install/setup.bash
ros2 run drone_bridge telemetry_bridge
```

У другому терміналі після `source install/setup.bash`:

```bash
ros2 launch drone_bridge bridge.launch.py
ros2 node list
```

`ros2 node list` містить `telemetry_bridge`.

### 7. Демонстрація публікації

Вузол публікує кадр лише тоді, коли його викликає джерело MAVLink. Для
демонстрації створіть `~/ros2_ws/demo_driver.py`:

```python
from types import SimpleNamespace

import rclpy

from drone_bridge.telemetry_bridge import TelemetryBridge

rclpy.init()
node = TelemetryBridge()
battery = SimpleNamespace(
    get_type=lambda: 'BATTERY_STATUS',
    get_srcSystem=lambda: 7,
    battery_remaining=87,
)
node.create_timer(0.1, lambda: node.publish_message(battery))
try:
    rclpy.spin(node)
finally:
    node.destroy_node()
    rclpy.shutdown()
```

Запуск (після `source install/setup.bash`):

```bash
python3 ~/ros2_ws/demo_driver.py
```

У третьому терміналі: `ros2 topic hz /drone/telemetry` показує ~10 Гц,
`ros2 topic echo /drone/telemetry` — JSON із полями `type`, `system_id`, `battery`.

## Очікуваний результат

- Пакет `drone_bridge` з вузлом `telemetry_bridge`.
- `bridge_logic.py` з `mavlink_to_dict`, що проходить check без ROS2.
- Launch-файл `bridge.launch.py`.
- Запис `ros2 topic echo` з JSON-телеметрією.

## Перевірка

Спочатку контракт без ROS2 — перевірте еталон курсу і власну теку:

```bash
cd <репозиторій>
python 09-ros2/checks/check_lab.py --target 09-ros2/solution
python 09-ros2/checks/check_lab.py --target ~/ros2_ws/src/drone_bridge/drone_bridge
```

Очікуваний вивід обох команд:

```text
PASS: конвертація тестується без ROS2, вузол має потрібну структуру
```

Потім перевірте живий потік за кроками 6–7: `ros2 topic hz /drone/telemetry`
показує ~10 Гц, `ros2 topic echo` — опубліковані словники.

## Розбір збоїв

- `Package 'drone_bridge' not found` — не виконано `source install/setup.bash`.
- `ModuleNotFoundError: No module named 'bridge_logic'` при `ros2 run` — вузол
  у пакеті має імпортувати `from .bridge_logic import ...`, а не плоско.
- Підписник не отримує даних — різні `ROS_DOMAIN_ID` або QoS.
- Вузол не завершується — немає `destroy_node`/`shutdown`.
