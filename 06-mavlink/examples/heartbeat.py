from pymavlink import mavutil

conn = mavutil.mavlink_connection('udp:127.0.0.1:14550')
conn.wait_heartbeat()
print(f"Heartbeat from system {conn.target_system}")
