from pymavlink import mavutil

conn = mavutil.mavlink_connection('udp:127.0.0.1:14550')
while True:
    msg = conn.recv_match(type='BATTERY_STATUS', blocking=True)
    print(f"Battery: {msg.battery_remaining}%")
