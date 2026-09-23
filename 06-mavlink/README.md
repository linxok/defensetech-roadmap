# 06. MAVLink: протокол і gateway

> Статус: complete

Розібрати MAVLink 2 до рівня байтів і побудувати gateway, який перетворює потік автопілота на JSON для WebSocket-клієнтів. Окремий фокус — безпека й надійність: signing проти підміни кадрів, `COMMAND_ACK` як єдиний доказ виконання команди, діалекти й невідомі повідомлення. Модуль спирається на `pymavlink` і дає контракт, який далі використовують capstone та модулі керування.

## Що потрібно зрозуміти

### Кадр MAVLink 2

| Поле | Байтів | Сенс |
|---|---|---|
| magic | 1 | `0xFD` — MAVLink 2; `0xFE` — застарілий MAVLink 1 |
| payload length | 1 | 0–255 після відкидання хвостових нулів |
| incompat flags | 1 | біт `0x01` — кадр підписаний; невідомий біт → кадр відкидають |
| compat flags | 1 | розширення, які можна ігнорувати |
| sequence | 1 | нумерація для оцінки втрат, не гарантія доставки |
| system id, component id | 2 | відправник у топології MAVLink |
| message id | 3 | little-endian, 24 біти — тільки в MAVLink 2 |
| payload | 0–255 | порядок полів визначає XML, а не C-структура |
| checksum | 2 | CRC-16/MCRF4XX, little-endian |
| signature | 0 або 13 | лише якщо виставлений біт `0x01` |

- Хвостові нулі payload не передаються (trailing zero truncation): приймач дозаповнює payload нулями до очікуваної довжини повідомлення, тому довжина кадру ніколи не дорівнює `sizeof` структури.
- CRC рахується від байтів від payload length до кінця payload і завершується байтом `crc_extra` з опису конкретного повідомлення; `crc_extra` — не хеш, а число зі специфікації повідомлення.

### Команди, ACK і стан

- `COMMAND_LONG` несе 7 float-параметрів і код команди в полі `command`; `COMMAND_INT` — цілочисельні координати в 1e7 градусів для точніших місій.
- Виконання підтверджує `COMMAND_ACK.result`: `MAV_RESULT_ACCEPTED` (0) — прийнято, `MAV_RESULT_IN_PROGRESS` (5) — триватиме, `MAV_RESULT_DENIED` (2) і `MAV_RESULT_FAILED` (4) — відмова; без ACK у межах таймауту команда вважається невиконаною.
- `HEARTBEAT` (1 Гц) несе `type` (тип апарата), `autopilot`, `base_mode` з бітом `MAV_MODE_FLAG_SAFETY_ARMED` (128), `custom_mode` (режим польоту) і `system_status`; тиша понад 3 с — сигнал розриву лінку.
- `GLOBAL_POSITION_INT`: `lat`/`lon` у 1e7 градусів, `alt`/`relative_alt` у міліметрах, `hdg` у сантиградусах, де `65535` означає «курс невідомий» — саме це перетворює gateway у JSON-контракт із `lab.md`.

### Безпека й діалекти

- Підпис MAVLink 2: 13 байт = 8-бітний link id + 48-бітний timestamp у 10-мкс тіках + 6 байт SHA-256 від `secret_key ‖ кадр без підпису ‖ link_id ‖ timestamp`; дані не шифруються, але підміна й повтор виключаються.
- Replay-захист тримається на timestamp: приймач відкидає кадри з часом, старшим за останній прийнятий; обидві сторони мусять мати однаковий ключ і link id.
- Діалекти впорядковані залежностями: `minimal.xml` → `common.xml` → `ardupilotmega.xml` (розширення ArduPilot); повідомлення з чужого діалекту без нього не парситься.
- Невідомий message id — норма: pymavlink віддає об’єкт `MAVLink_unknown`, і gateway має його проігнорувати, а не падати; невідомий incompat-біт змушує кадр відкинути.
- MAVLink 1 залишається підмножиною за змістом: якщо message id вкладаються в 8 біт і немає extension-полів, той самий потік приймається як MAVLink 2 без втрат.

### Gateway: архітектура

- Читання джерела — окрема задача з `asyncio.to_thread` навколо `recv_match(blocking=True, timeout=1.0)`, щоб event loop не чекав на сокет.
- `TelemetryHub` тримає набір клієнтів під `asyncio.Lock` і розсилає кадри через `asyncio.gather(..., return_exceptions=True)`; повільний клієнт видаляється, решта отримує дані.
- Backpressure: якщо WebSocket-клієнт не встигає, черга broadcast не має зростати в пам’яті — обмежуйте її та відключайте відстаючих.
- Graceful shutdown: `SIGINT`/`SIGTERM` → `asyncio.Event` → скасування reader-задачі → `gather` → `connection.close()`; без цього процес лишає сокет і SITL-з’єднання відкритими.
- JSON-контракт версіонується: поле `type` і набір полів фіксують схему, бо `NaN`/`Infinity` у JSON невалідні (RFC 8259) і ламають `JSON.parse` на клієнті.

## Контрольні питання

1. Скільки байтів має кадр MAVLink 2 із payload 28 байт без підпису і з підписом?
2. Що gateway має зробити з `PING` і з повідомленням невідомого типу, щоб не порушити контракт?
3. Який біт incompat flags відповідає за підпис і що станеться з кадром, у якому виставлений невідомий біт?
4. Які три частини підпису і які саме байти потрапляють у SHA-256?
5. Чим `MAV_RESULT_IN_PROGRESS` відрізняється від `MAV_RESULT_ACCEPTED` і як це впливає на очікування ACK?
6. Що означає `hdg == 65535` і як це має відобразитися в JSON?
7. Який симптом у логах і на клієнті, якщо SITL слухає не той UDP-порт?

## Очікуваний результат

- `mavlink_gateway.py` з функцією `mavlink_to_telemetry` і класом `TelemetryHub`, що проходить `python 06-mavlink/checks/check_lab.py --target <тека>`.
- Живий потік JSON у `examples/websocket_client.html`: `HEARTBEAT` і `GLOBAL_POSITION_INT` з оновленням щосекунди.
- У коді немає `asyncio.wait(` із корутинами і немає `recv_match` без `asyncio.to_thread`.
- Розуміння, як увімкнути signing і чому без однакового ключа з’являється `MAVError: Invalid signature`.

## Зв'язок з capstone

Рядок `gateway/` у таблиці «Архітектура» `capstone/README.md` — це той самий сервіс, лише замість WebSocket він робить HTTP POST у backend; розділ «Контракт» показує фінальний JSON-кадр. Розділ «Що далі» пропонує підключити реальний flight controller (`MAVLINK_SOURCE=udp:0.0.0.0:14550`) — саме після цього модуля це стає механічною заміною джерела.

## Типові помилки

- `MAVError: invalid MAVLink CRC in msgID 33 0x0000 should be 0xc3e3` — CRC раховано від magic-байта або без `crc_extra`; для `GLOBAL_POSITION_INT` `crc_extra=104`.
- `MAVError: invalid MAVLink prefix 'b'` — у потоці сміття: не той baudrate, порт або джерело не в MAVLink-режимі.
- `MAVError: Invalid signature` — інший ключ, link id або неприпустимо старий timestamp у підписі.
- `TimeoutError` (або лог `no heartbeat from udp:127.0.0.1:14550`) — SITL і gateway слухають різні порти; типове джерело — `udp:127.0.0.1:14550`.
- `TypeError: Passing coroutines is forbidden, use tasks explicitly.` — `asyncio.wait` замість `asyncio.gather` для списку корутин.
- `SyntaxError: Unexpected token 'N'` на клієнті — у JSON потрапив `NaN`/`Infinity`, які не є валідним JSON.
- `OSError: [Errno 98] Address already in use` — порт 8765 зайнятий попереднім запуском gateway.

## Первинні джерела

- [MAVLink: Message Serialization](https://mavlink.io/en/guide/serialization.html) — байтовий формат, CRC, підпис.
- [MAVLink: Message Signing](https://mavlink.io/en/guide/message_signing.html) — ключі, link id, timestamp, replay-захист.
- [MAVLink: Common Messages](https://mavlink.io/en/messages/common.html) — поля `HEARTBEAT`, `GLOBAL_POSITION_INT`, `COMMAND_*`, `MAV_RESULT_*`.
- [mavlink/message_definitions](https://github.com/mavlink/mavlink/tree/master/message_definitions/v1.0) — XML-джерела діалектів і `crc_extra`.
- [pymavlink: mavutil.py](https://github.com/ArduPilot/pymavlink/blob/master/mavutil.py) — `mavlink_connection`, `recv_match`, робота з діалектами.
- [RFC 8259: JSON](https://www.rfc-editor.org/rfc/rfc8259) — чому `NaN` і `Infinity` недопустимі в JSON.
- [RFC 6455: WebSocket](https://www.rfc-editor.org/rfc/rfc6455) — кадри, закриття, причини розриву.

## Куди далі

Лабораторна: `lab.md`; далі `detailed-guide.md` і `checklist.md`. Керування на основі цього протоколу — модуль `07-ardupilot`, серверний бік потоку — `10-backend`, відображення — `14-ground-control`.
