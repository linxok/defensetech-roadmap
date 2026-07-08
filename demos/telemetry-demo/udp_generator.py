import socket
import json
import time
import random

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

i = 0
while True:
    payload = json.dumps({
        'drone_id': 'demo-001',
        'lat': 50.45 + random.uniform(-0.001, 0.001),
        'lon': 30.52 + random.uniform(-0.001, 0.001),
        'alt': 100 + random.randint(-5, 5),
        'battery': 87 - (i % 20),
        'ts': time.time()
    })
    sock.sendto(payload.encode(), ('127.0.0.1', 14550))
    print(f'Sent: {payload}')
    time.sleep(1)
    i += 1
