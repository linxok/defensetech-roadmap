from pymavlink import mavutil

conn = mavutil.mavlink_connection('tcp:127.0.0.1:5762')
conn.wait_heartbeat()
conn.set_mode('RTL')
print("RTL command sent")
