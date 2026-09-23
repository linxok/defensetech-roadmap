#!/usr/bin/env python3
"""Надсилає тестові датаграми на UDP-порт моста `udp_ws_bridge.py`.

Міст не відповідає на UDP, тому читання відповіді обмежено таймаутом:
без `settimeout` виклик `recvfrom` блокувався б назавжди.

Запуск:

    python udp_client.py --host 127.0.0.1 --port 14550
"""

from __future__ import annotations

import argparse
import json
import socket
from typing import Any

VALID_PACKET: dict[str, Any] = {
    'drone_id': 'd1',
    'type': 'ATTITUDE',
    'roll': 0.1,
    'pitch': -0.2,
    'yaw': 1.57,
}

MALFORMED_PACKET = b'{"type": "ATTITUDE"'


def send_datagram(sock: socket.socket, address: tuple[str, int], payload: bytes) -> None:
    sock.sendto(payload, address)
    print(f'sent {len(payload):>3} bytes: {payload[:48]!r}')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=14550)
    parser.add_argument('--timeout', type=float, default=2.0)
    args = parser.parse_args()

    address = (args.host, args.port)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(args.timeout)

        print('valid packet:')
        send_datagram(sock, address, json.dumps(VALID_PACKET).encode('utf-8'))

        print('malformed packet (broken JSON):')
        send_datagram(sock, address, MALFORMED_PACKET)

        try:
            reply, reply_addr = sock.recvfrom(1024)
        except TimeoutError:
            print('no UDP reply within timeout — bridge is one-way, check its journal')
        else:
            print(f'reply from {reply_addr}: {reply!r}')


if __name__ == '__main__':
    main()
