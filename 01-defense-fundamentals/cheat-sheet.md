# Cheat Sheet 01: Основи DefenseTech і архітектура UAV

- `sim_vehicle.py -v ArduCopter --console --map` — SITL з консоллю
- `--out=udp:127.0.0.1:14550` — додатковий вихід для GCS
- Режими Copter: STABILIZE, ALT_HOLD, LOITER, GUIDED, AUTO, RTL, LAND
- `MAV_CMD_NAV_TAKEOFF`, `MAV_CMD_NAV_LAND`, `MAV_CMD_COMPONENT_ARM_DISARM`
- ESC протоколи: PWM 50–400 Гц, OneShot, DShot150/300/600
