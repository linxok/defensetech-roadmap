# 09. ROS2: мости телеметрії

> Статус: complete

Побудувати ROS2-вузол, який перетворює MAVLink-повідомлення на JSON у топік `drone/telemetry`, тримаючи всю логіку конвертації поза rclpy. Модуль пояснює, як DDS, QoS і життєвий цикл вузла впливають на те, чи дійде кадр до підписника. Артефакт — пакет `drone_bridge`, який збирається `colcon`, запускається `ros2 run` і перевіряється офлайн без ROS2.

## Що потрібно зрозуміти

- ROS2 Humble звʼязує вузли через DDS без центрального брокера: публікація йде напряму, виявлення — через UDP multicast. Типовий RMW у стандартних бінарниках — Fast DDS (`rmw_fastrtps_cpp`); перемкнути на CycloneDDS можна змінною `RMW_IMPLEMENTATION=rmw_cyclonedds_cpp`, а подивитися активний — через `ros2 doctor --report`.
- `ROS_DOMAIN_ID` (типово 0) ізолює групи вузлів у спільній мережі, `ROS_LOCALHOST_ONLY=1` обмежує трафік локальною машиною.
- Топік — асинхронний many-to-many потік, сервіс — один запит і одна відповідь, дія — довготривала задача з feedback. Для безперервної телеметрії доречний топік `std_msgs/msg/String` із JSON.
- QoS визначає сумісність публікатора й підписника: `reliability` (`reliable`/`best_effort`), `durability` (`volatile`/`transient_local`), `history` (`keep_last`, глибина 10). Для 50-Гц телеметрії — `best_effort` і `keep_last(10)`, для команд — `reliable`, для «останнього стану» новому підписнику — `transient_local`.
- Несумісний QoS не дає помилки: `reliable`-публікатор із `best_effort`-підписником сумісні, а `best_effort`-публікатор із `reliable`-підписником — ні, і підписник просто мовчить.
- Життєвий цикл rclpy: `rclpy.init()` → вузол → `create_publisher(String, 'drone/telemetry', 10)` → `rclpy.spin(node)`, а в `finally` — `destroy_node()` і `rclpy.shutdown()`.
- Пакет `ament_python`: `package.xml`, `setup.py` з `entry_points['console_scripts']`, `setup.cfg`; збірка — `colcon build --packages-select drone_bridge`, після чого в кожному терміналі `source install/setup.bash`.
- Чиста логіка в `bridge_logic.py` не імпортує rclpy: `mavlink_to_dict(message)` повертає `dict` або `None`, тому конвертація тестується звичайним pytest у CI, а вузол займається лише інтеграцією.
- Конвертація: `GLOBAL_POSITION_INT.lat/lon` — градуси × 1e7, `alt` — міліметри, `hdg` — соті градуса, де `65535` означає «курс невідомий»; `HEARTBEAT` не входить у `TRACKED_TYPES` і повертає `None`.
- micro-ROS ставить ROS2 на мікроконтролер, але на борту частіше лишають MAVLink, а міст тримають на companion-компʼютері — саме так, як у лабораторній.
- `colcon build` складає результат в `install/`, який підключається як overlay до `/opt/ros/humble`: без `source install/setup.bash` у поточному терміналі вузол не знайдеться навіть після успішної збірки.
- `ros2 run` достатній для одного вузла; `ros2 launch` потрібен, коли вузлів кілька або треба передати параметри — launch-файл і є точкою входу для оператора.
- Вузол за замовчуванням крутиться в single-threaded executor: синхронний колбек блокує решту. Для моста це означає, що читання MAVLink і публікацію не можна робити в одному довгому виклику.
- Діагностика потоку: `ros2 topic info --verbose` показує типи й QoS, `ros2 topic hz` — фактичну частоту, `ros2 topic echo` — вміст; ці три команди закривають питання «чи йде публікація».

- `publish` не чекає на підписників: DDS ставить повідомлення у власні черги, тому втрати й затримки видно не в коді, а в QoS і статистиці `ros2 topic hz`.
- Імʼя вузла задається при створенні (`super().__init__('telemetry_bridge')`) і саме його показує `ros2 node list`; передбачувані імена спрощують діагностику.
- JSON у `String` — свідомий компроміс: не треба генерувати власні типи, але схему не перевіряє DDS; для продакшн-повідомлень краще власний `.msg`.
- `ros2 interface show std_msgs/msg/String` підтверджує контракт: одне поле `data`, тому вся структура телеметрії живе в JSON, а не в типі.

## Анатомія кадру

1. Джерело MAVLink формує кадр — драйвер поруч із вузлом або pymavlink у тесті.
2. `mavlink_to_dict` конвертує кадр у словник, не знаючи нічого про rclpy.
3. Вузол кладе JSON у `std_msgs/msg/String` і викликає `publish`.
4. DDS доставляє повідомлення підписникам згідно з QoS і доменом.
5. Підписник бачить потік; діагностика — `ros2 topic hz` та `ros2 topic echo`.
6. Кожен крок має власний симптом збою: від `ModuleNotFoundError` до тиші через несумісний QoS.
7. Перевірити контракт без ROS2: `checks/check_lab.py --target <тека>` із `FakeMessage`.
8. Повторити живий запуск після `colcon build` і `source`, щоб офлайн-PASS і реальна публікація не розійшлися.

## Контрольні питання

1. Який QoS-профіль доречний для телеметрії 50 Гц і чим це підтвердити через `ros2 topic info --verbose` та `ros2 topic hz`?
2. Як перевірити конвертацію в CI, де немає ROS2, і який вивід `checks/check_lab.py` це доводить?
3. Що станеться без `destroy_node()`/`rclpy.shutdown()` і як це ловить перевірка?
4. Як дізнатися, який RMW використовує система, і що змінить `RMW_IMPLEMENTATION`?
5. Назвіть дві причини, чому підписник не бачить повідомлень при живому публікаторі.
6. Чим топік відрізняється від сервісу на рівні команд `ros2 topic list` і `ros2 service list`?
7. Як підтвердити, що публікація йде з частотою близько 10 Гц?
8. Чому `HEARTBEAT` навмисно повертає `None`?
9. Куди `colcon build` кладе результат і чому без `source install/setup.bash` пакет не запускається?
10. Чим небезпечний довгий синхронний колбек і чому це критично саме для моста?

## Очікуваний результат

Пакет `drone_bridge`: `solution/bridge_logic.py`, `solution/telemetry_bridge.py`, `solution/setup.py` і launch-файл. Команда `python 09-ros2/checks/check_lab.py --target 09-ros2/solution` друкує `PASS: конвертація тестується без ROS2, вузол має потрібну структуру`. У живому запуску `ros2 node list` показує `telemetry_bridge`, `ros2 topic hz /drone/telemetry` — близько 10 Гц, а `ros2 topic echo` — JSON із `type`, `system_id` і полями кадру.

## Зв'язок з capstone

`capstone/README.md` → «Архітектура»: gateway перетворює MAVLink на JSON — це той самий поділ «протокол ↔ публікація», що `bridge_logic` ↔ rclpy-вузол. «Що далі» п. 3 — CV-сервіс як споживач відео: ROS2-міст може віддавати йому телеметрію, не змінюючи backend.

## Межі модуля

- Формат MAVLink і gateway з ретраями — модулі 06 і 10; тут важливий лише контракт повідомлення.
- Керування польотом (команди, режими) — модуль 07.
- Компʼютерний зір як споживач телеметрії — модуль 12.
- Безпека DDS, тюнінг executorʼів і власні типи повідомлень — поза межами курсу.
- Міграція ROS1 → ROS2 і MAVROS — окремі теми; тут використовується нативний rclpy.

## Як перевіряється

- `python checks/check_lab.py --target <тека>` імпортує `bridge_logic.py`: будь-який імпорт rclpy у логіці валить перевірку.
- `GLOBAL_POSITION_INT(lat=504501000, lon=305234000, alt=120000, hdg=9000)` мусить дати `lat ≈ 50.4501`, `alt = 120.0`, `heading = 90.0`.
- `BATTERY_STATUS(battery_remaining=87)` дає `battery == 87`, а `HEARTBEAT` — `None` (у топік не публікується).
- У тексті вузла обовʼязкові `create_publisher`, `drone/telemetry`, `destroy_node`, `rclpy.spin`.
- Еталон — `--target 09-ros2/solution`; після збірки той самий контракт перевіряється на теці пакета.
- Живий потік (`ros2 topic hz` і `echo`) — ручний крок, який CI не замінює.

## Типові помилки

- `ModuleNotFoundError: No module named 'bridge_logic'` при `ros2 run` — усередині пакета імпорт має бути відносним: `from .bridge_logic import mavlink_to_dict`.
- `Package 'drone_bridge' not found` — у терміналі не виконано `source install/setup.bash`.
- `FAIL: bridge_logic не імпортується без ROS2: ModuleNotFoundError: No module named 'rclpy'` — логіку змішали з інтеграцією.
- `FAIL: у вузлі немає destroy_node` — прибирання вузла пропущено або винесено за межі `finally`.
- Підписник мовчить при працюючому публікаторі: різні `ROS_DOMAIN_ID` або несумісний QoS (`best_effort` публікатор і `reliable` підписник).
- `ros2 topic hz` показує `no new messages`, хоча вузол запущено: він публікує лише у відповідь на MAVLink-кадри, тож для демонстрації потрібне джерело, як у кроці 7 лабораторної.
- Різні типи повідомлень на одному імені топіка не матчаться: `ros2 topic info` показує інший type, і дані не доходять.
- `TypeError: Object of type bytes is not JSON serializable` — у словник потрапили байти з кадру; конвертуйте поля явно, як у `mavlink_to_dict`.
- `ros2 topic echo` показує порожні кадри — публікується `String()` без `data`; перевірте, що виконано `msg.data = json.dumps(...)`.
- Після `Ctrl+C` летить стек `KeyboardInterrupt` від rclpy — `spin` не обгорнуто в `try/finally`, тому вузол не прибирається.

## Первинні джерела

- [ROS2 Humble Concepts](https://docs.ros.org/en/humble/Concepts.html) — вузли, топіки, DDS.
- [About QoS settings](https://docs.ros.org/en/humble/Concepts/Intermediate/About-Quality-of-Service-Settings.html) — політики та їхня сумісність.
- [About different middleware vendors](https://docs.ros.org/en/humble/Concepts/Intermediate/About-Different-Middleware-Vendors.html) — Fast DDS, CycloneDDS, `RMW_IMPLEMENTATION`.
- [rclpy API](https://docs.ros.org/en/humble/p/rclpy/) — `Node`, `Publisher`, `spin`, `shutdown`.
- [Creating a ROS2 package](https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Creating-Your-First-ROS2-Package.html) — `package.xml`, `setup.py`, colcon.
- [micro-ROS](https://micro.ros.org/) — ROS2 на MCU.
- [colcon tutorial](https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Colcon-Tutorial.html) — workspace, overlay, `source install/setup.bash`.

## Куди далі

`lab.md` — покрокове створення пакета й перевірка офлайн; далі `detailed-guide.md` і `checklist.md`. За курсом наступний модуль — 10 (backend), який споживає ту саму телеметрію через HTTP і WebSocket. Міст навмисно мінімальний: підписка, сервіси й власні типи повідомлень — у `mini-project.md`.
