# Cheat Sheet 07: ArduPilot: керування польотом

- `conn.set_mode_apm("GUIDED")` або `set_mode_send(sys, flag, 4)`
- `conn.arducopter_arm()` / `MAV_CMD_COMPONENT_ARM_DISARM`
- `MAV_CMD_NAV_TAKEOFF` (22), `MAV_CMD_NAV_LAND` (21), `MAV_CMD_NAV_RETURN_TO_LAUNCH` (20)
- `MAV_RESULT_ACCEPTED` (0), `MAV_RESULT_TEMPORARILY_REJECTED` (1), `MAV_RESULT_DENIED` (2)
- `FS_THR_ENABLE=1`, `FS_GCS_ENABLE=1`, `FENCE_ENABLE=1`, `FENCE_ACTION=1`
- `sim_vehicle.py -v ArduCopter` (SITL сам слухає TCP 5762; другий порт — `--out=tcpin:0.0.0.0:5763`)
