import asyncio
import json
import os
import socket
import requests

BACKEND_URL = os.environ.get('BACKEND_URL', 'http://backend:8000')

async def udp_to_backend():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', 14550))
    sock.setblocking(False)
    loop = asyncio.get_running_loop()
    while True:
        data, _ = await loop.sock_recvfrom(sock, 1024)
        try:
            msg = json.loads(data.decode())
            requests.post(f'{BACKEND_URL}/telemetry', json=msg, timeout=2)
            print(f'Forwarded: {msg}')
        except Exception as e:
            print(f'Error: {e}')

asyncio.run(udp_to_backend())
