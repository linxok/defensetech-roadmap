# Cheat Sheet 06: MAVLink: протокол і gateway

- `conn.wait_heartbeat(timeout=30)` — очікування вузла
- `conn.recv_match(type="GLOBAL_POSITION_INT", blocking=True, timeout=1)`
- `msg.get_type()`, `msg.get_srcSystem()`, `msg.get_srcComponent()`
- `conn.mav.command_long_send(...)` + очікування `COMMAND_ACK`
- GLOBAL_POSITION_INT: lat/lon ×1e7, alt/hdg ×1e3/×1e2
- Порти: 14550 UDP (GCS), 14551 (другий клієнт), 5760 TCP (SITL)
