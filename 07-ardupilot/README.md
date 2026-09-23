# 07. ArduPilot: керування польотом

> Статус: complete

Керувати SITL через pymavlink: режими, ARM, зліт, місії, RTL — і зробити це безпечно, з ACK і таймаутами.

## Що потрібно зрозуміти

- Режими Copter: STABILIZE, ALT_HOLD, LOITER, GUIDED, AUTO, RTL, LAND. GUIDED (custom mode 4) потрібен для команд керування точкою.
- ARM — команда `MAV_CMD_COMPONENT_ARM_DISARM`; без успішного ACK вважати дрон озброєним заборонено.
- Зліт: `MAV_CMD_NAV_TAKEOFF` з висотою; після зльоту позиція керується `SET_POSITION_TARGET_LOCAL_NED` у GUIDED.
- Місії: `MISSION_COUNT` → `MISSION_REQUEST_INT` → `MISSION_ITEM_INT` → `MISSION_ACK`. Типова помилка — не дочекатися MISSION_ACK.
- RTL повертає на home-позицію і сідає; домашня точка фіксується при ARM, тому зміна home у польоті — окрема команда.
- Failsafe: `FS_THR_ENABLE=1` (втрата RC), `FS_GCS_ENABLE` (втрата GCS), `FS_BATT_VOLTAGE`, `FENCE_ENABLE` + `FENCE_ACTION=1` (RTL).
- Lua-скрипти на борту (`SCR_ENABLE`) дозволяють кастомну логіку без перезбірки прошивки — але кожен скрипт має таймаут і не блокує loop.
- Сигнали безпеки на землі: пропелери знято до першого ARM, motors disarmed у SITL за замовчуванням.

## Контрольні питання

1. Який режим потрібен для takeoff у Copter і як він задається?
2. Як виглядає повний обмін для завантаження місії?
3. Які параметри відповідають за RTL при втраті RC і GCS?
4. Чому команду без COMMAND_ACK не можна вважати виконаною?
5. Як перевірити failsafe в SITL, не маючи пульта?

## Очікуваний результат

REST API над SITL з ін’єкцією з’єднання і тестами (`solution/ardupilot_api.py`) + перевірений failsafe-сценарій.

## Зв'язок з capstone

Крок 7: команди capstone (ARM/takeoff/RTL) — той самий рівень; REST API можна підключити як сервіс керування.

## Типові помилки

- Створювати MAVLink-з’єднання при імпорті модуля: без SITL сервіс не стартує.
- Слати takeoff без попереднього ARM і mode GUIDED — команда ігнорується.
- Викликати `recv_match` без timeout у циклі очікування ACK — вічне зависання.
- Не перевіряти `result` у COMMAND_ACK: відмова виглядає як успіх.

## Первинні джерела

- [ArduPilot Copter Docs](https://ardupilot.org/copter/) — режими, параметри, місії
- [ArduPilot Dev Docs](https://ardupilot.org/dev/index.html) — SITL, Lua, архітектура
- [MAVLink Common Messages](https://mavlink.io/en/messages/common.html) — команди та їхні параметри
- [pymavlink examples](https://github.com/ArduPilot/pymavlink/tree/master/examples) — ready-код для ARM, takeoff, mission
- [ArduPilot parameter reference](https://ardupilot.org/copter/docs/parameters.html) — FS_*, FENCE_*, WPNAV_*

## Куди далі

Далі: `lab.md` → `detailed-guide.md` → `checklist.md`.
