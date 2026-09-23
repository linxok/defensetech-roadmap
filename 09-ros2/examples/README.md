# Приклади 09: ROS2: мости телеметрії

У `examples/` — publisher, subscriber і launch. Еталон з тестованою логікою: `solution/`.

`rclpy` не ставиться через pip — він входить до складу ROS2 Humble. Спершу в
кожному терміналі:

```bash
source /opt/ros/humble/setup.bash
```

Запуск прикладів (з кореня репозиторію, кожен у своєму терміналі):

```bash
python3 09-ros2/examples/telemetry_publisher.py     # 10 Гц у /drone/telemetry
python3 09-ros2/examples/telemetry_subscriber.py    # друкує отримані кадри
ros2 topic hz /drone/telemetry
```

`launch.py` — приклад для теки `drone_bridge/launch/` створеного пакета
(див. `lab.md`, кроки 4–6); після `colcon build` його запускають так:

```bash
ros2 launch drone_bridge bridge.launch.py
```

Контракт лабораторної перевіряється окремо:

```bash
python3 09-ros2/checks/check_lab.py --target 09-ros2/solution
```
