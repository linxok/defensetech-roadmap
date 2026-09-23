# Ресурси 06: MAVLink: протокол і gateway

Головний список джерел модуля. Первинні джерела — обов'язкові,
решта — за потреби.

## Первинні джерела

- [MAVLink Developer Guide](https://mavlink.io/en/) — протокол, guide, діалекти
- [MAVLink Serialization](https://mavlink.io/en/guide/serialization.html) — формат кадру, CRC, підпис
- [Common Message Set](https://mavlink.io/en/messages/common.html) — HEARTBEAT, GLOBAL_POSITION_INT, COMMAND_LONG, PARAM_*
- [pymavlink source](https://github.com/ArduPilot/pymavlink) — mavutil, mavlink_connection, діалекти
- [MAVSDK docs](https://mavsdk.mavlink.io/main/en/) — високорівневий клієнт замість ручного протоколу

## Додатково

- QGroundControl MAVLink Inspector — живий розбір повідомлень
- ArduPilot: MAVLink несумісності — https://ardupilot.org/dev/docs/mavlink-basics.html

Принцип: якщо переказ суперечить специфікації — правда в специфікації.
