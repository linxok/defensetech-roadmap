# 09. ROS2: мости телеметрії

> Статус: complete

Побудувати ROS2-вузол, який публікує телеметрію дрона, розділивши чисту логіку та інтеграцію з rclpy, щоб код тестувався без ROS2.

## Що потрібно зрозуміти

- ROS2 Humble: вузли, топіки, сервіси, дії; комунікація через DDS (CycloneDDS за замовчуванням), без центрального брокера.
- QoS: `best_effort` для високочастотної телеметрії, `reliable` для команд, `transient_local` для «останнього стану» новим підписникам.
- Пакет `ament_python`: `package.xml`, `setup.py`, `ros2 pkg create`, `colcon build`, `source install/setup.bash`.
- rclpy-вузол має коректно завершуватися: `destroy_node()` і `rclpy.shutdown()` у `finally`.
- Чисту логіку (конвертація MAVLink → dict) тримайте поза rclpy — тоді вона тестується в CI без встановленого ROS2.
- Launch-файл описує кілька вузлів з параметрами; для одного вузла достатньо `python -m`-запуску.
- micro-ROS дає ROS2 на мікроконтролерах — але на борту дрона частіше зустрічається MAVLink + ROS2-міст на companion.

## Контрольні питання

1. Який QoS обрати для 50-Гц телеметрії і чому?
2. Як протестувати конвертацію без встановленого ROS2?
3. Що станеться, якщо не викликати `destroy_node()`?
4. Чим топік відрізняється від сервісу в ROS2?
5. Як перевірити, що публікація справді йде?

## Очікуваний результат

ROS2-пакет `drone_bridge` з вузлом публікації та чистою логікою конвертації (`solution/bridge_logic.py`).

## Зв'язок з capstone

Крок 9: ROS2-міст можна підключити до capstone як окремий споживач телеметрії (наприклад, для CV-конвеєра).

## Типові помилки

- Імпортувати rclpy у модулі з логікою — тести вимагають повного ROS2.
- Публікувати без перевірки `publish()` у циклі з високою частотою без backpressure.
- Забути `source install/setup.bash` — новий термінал не бачить пакет.
- Змішувати повідомлення різних типів в одному топіку.

## Первинні джерела

- [ROS2 Humble Tutorials](https://docs.ros.org/en/humble/Tutorials.html) — вузли, топіки, launch
- [rclpy API](https://docs.ros.org/en/humble/p/rclpy/) — Node, Publisher, Subscription
- [ROS2 QoS design](https://docs.ros.org/en/humble/Concepts/Intermediate/About-Quality-of-Service-Settings.html) — політики надійності
- [micro-ROS](https://micro.ros.org/) — ROS2 на MCU
- [ROS Discourse](https://discourse.ros.org/) — практичні питання

## Куди далі

Далі: `lab.md` → `detailed-guide.md` → `checklist.md`.
