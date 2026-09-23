# 06. MAVLink: протокол і gateway

> Статус: complete

Розібрати формат MAVLink 2 до байтів, навчитися писати gateway, який перетворює потік у телеметрію, і закрити прогалини безпеки: signing, failsafe, геозони.

## Що потрібно зрозуміти

- MAVLink 2: magic `0xFD`, payload length, incompat/compat flags, sequence, system id, component id, 24-бітний message id, payload (0–255 байт), CRC-16/MCRF4XX, опційний 13-байтний підпис.
- Trailing zero truncation: хвіст payload із нулів не передається, тому довжина кадру не дорівнює розміру структури повідомлення.
- crc_extra: кожне повідомлення має власне значення CRC_EXTRA з XML-опису (наприклад, GLOBAL_POSITION_INT — 104, HEARTBEAT — 50).
- HEARTBEAT кожну секунду — індикатор живого вузла; `base_mode` і `custom_mode` кодують режим польоту.
- Команди: `COMMAND_LONG`/`COMMAND_INT` + `COMMAND_ACK` з result; без очікування ACK команда вважається невиконаною.
- MAVLink signing: 48-бітний link id, timestamp і 6 байт SHA-256 від кадру з ключем. Дані не шифруються, але підробка виключається.
- Failsafe/geofence: `FS_THR_ENABLE` (втрата RC), `FS_BATT_*`, `FENCE_ENABLE`/`FENCE_ACTION`/`FENCE_RADIUS` — це частина контракту польотного ПЗ, а не «налаштування оператора».
- Діалекти: `common.xml` — базові повідомлення, `ardupilotmega.xml` — розширення; невідомі message id ігноруються, а не ламають парсер.

## Контрольні питання

1. Які байти входить до CRC і звідки береться crc_extra?
2. Що робить gateway з повідомленнями невідомого типу?
3. Як забезпечити, щоб повільний WebSocket-клієнт не блокував потік?
4. Що додає signing і від яких атак він НЕ захищає?
5. Які параметри забороняють зліт за межі геозони?

## Очікуваний результат

Асинхронний MAVLink gateway із JSON-контрактом, known-answer тестами та graceful shutdown (`solution/mavlink_gateway.py`).

## Зв'язок з capstone

Крок 6: gateway capstone — це той самий код із HTTP-відправкою в backend замість WebSocket; використовуйте його як основу.

## Типові помилки

- `asyncio.wait([c.send(...) for c in clients])` — корутини замість задач; у Python 3.12 це `RuntimeError`.
- `recv_match(blocking=True)` прямо в async-функції блокує event loop на секунди — потрібен `asyncio.to_thread`.
- Парсити CRC без crc_extra: частина кадрів «валідна» випадково.
- Слати JSON клієнтам без версії схеми: фронтенд ламається при зміні полів.

## Первинні джерела

- [MAVLink Developer Guide](https://mavlink.io/en/) — протокол, guide, діалекти
- [MAVLink Serialization](https://mavlink.io/en/guide/serialization.html) — формат кадру, CRC, підпис
- [Common Message Set](https://mavlink.io/en/messages/common.html) — HEARTBEAT, GLOBAL_POSITION_INT, COMMAND_LONG, PARAM_*
- [pymavlink source](https://github.com/ArduPilot/pymavlink) — mavutil, mavlink_connection, діалекти
- [MAVSDK docs](https://mavsdk.mavlink.io/main/en/) — високорівневий клієнт замість ручного протоколу

## Куди далі

Далі: `lab.md` → `detailed-guide.md` → `checklist.md`.
