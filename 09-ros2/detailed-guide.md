# Розширений гайд 09: ROS2: мости телеметрії

Цикл навчання — у `docs/learning-workflow.md`. Нижче — маршрут модуля.

## Порядок проходження

1. Встановіть ROS2 Humble за docs/setup.md.
2. Створіть пакет `drone_bridge` і зберіть `colcon build`.
3. Реалізуйте `bridge_logic.py` без rclpy (чиста функція).
4. Обгорніть логіку у вузол `telemetry_bridge.py`.
5. Перевірте потік: `ros2 topic echo /drone/telemetry`.
6. Запустіть `checks/check_lab.py` — логіка тестується без ROS2.

## Орієнтовний час

2 тижні (12–16 годин)

## Артефакти модуля

- пакет `drone_bridge`
- `bridge_logic.py` + тест
- запис `ros2 topic echo`

## Пастки цього модуля

- `source /opt/ros/humble/setup.bash` потрібен у кожному терміналі
- Ім’я топіку без ведучого слеша — норма для ROS2
- Вузол без `spin` не отримує callbacks
