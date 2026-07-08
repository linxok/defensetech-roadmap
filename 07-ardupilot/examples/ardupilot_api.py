from fastapi import FastAPI
from pymavlink import mavutil

app = FastAPI()
conn = mavutil.mavlink_connection('tcp:127.0.0.1:5762')
conn.wait_heartbeat()

@app.post('/arm')
def arm():
    conn.arducopter_arm()
    return {'status': 'armed'}

@app.post('/takeoff')
def takeoff(alt: float = 10.0):
    conn.set_mode('GUIDED')
    conn.mav.command_long_send(
        conn.target_system, conn.target_component,
        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0,
        0, 0, 0, 0, 0, 0, alt
    )
    return {'status': 'takeoff', 'alt': alt}

@app.post('/rtl')
def rtl():
    conn.set_mode('RTL')
    return {'status': 'rtl'}

@app.get('/status')
def status():
    msg = conn.recv_match(type='HEARTBEAT', blocking=True, timeout=5)
    return {'heartbeat': msg.to_dict() if msg else None}
