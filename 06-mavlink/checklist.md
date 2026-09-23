# Чекліст 06: MAVLink: протокол і gateway

Кожен пункт — команда або артефакт з об'єктивним результатом.
Самозвіт «зрозумів» не зараховується.

- [ ] `python checks/check_lab.py --target solution` проходить
- [ ] HEARTBEAT і GLOBAL_POSITION_INT видно в WebSocket-клієнті
- [ ] Парсер кадру витримує пошкоджений CRC (тест)
- [ ] Немає `asyncio.wait(` у коді gateway
- [ ] Failsafe RTL перевірено в SITL хоч раз

Повний прогін: `python scripts/run_lab_checks.py --module 06-mavlink`.
