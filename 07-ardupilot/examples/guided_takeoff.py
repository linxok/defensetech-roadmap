from pymavlink import mavutil

conn = mavutil.mavlink_connection('tcp:127.0.0.1:5762')
conn.wait_heartbeat()
conn.mav.set_mode_send(conn.target_system,
    mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED, 4)
conn.mav.command_long_send(conn.target_system, conn.target_component,
    mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, 0, 10)
print("Takeoff command sent")
