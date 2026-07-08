# Лабораторна робота 09: ROS2 Telemetry Bridge

## Мета

Створити ROS2-вузол, який підписується на telemetry topic і публікує її в інший формат для GCS.

## Передумови

- ROS2 Humble встановлено.
- Workspace `~/ros2_ws/src` створено.

## Кроки

### 1. Створення пакету

```bash
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_python drone_bridge --dependencies rclpy std_msgs
```

### 2. Publisher node

```python
import rclpy
from std_msgs.msg import String

rclpy.init()
node = rclpy.create_node('telemetry_publisher')
publisher = node.create_publisher(String, 'drone/telemetry', 10)

msg = String()
msg.data = '{"alt": 100, "battery": 87}'
publisher.publish(msg)
```

### 3. Subscriber node

```python
import rclpy
from std_msgs.msg import String

def callback(msg):
    print(f"Received: {msg.data}")

rclpy.init()
node = rclpy.create_node('telemetry_subscriber')
sub = node.create_subscription(String, 'drone/telemetry', callback, 10)
rclpy.spin(node)
```

### 4. Build

```bash
cd ~/ros2_ws
colcon build
source install/setup.bash
```

### 5. Launch

```bash
ros2 run drone_bridge telemetry_publisher
ros2 run drone_bridge telemetry_subscriber
```

## Очікуваний результат

- ROS2 пакет `drone_bridge`.
- Publisher і subscriber nodes.
- Launch file.
