"""Мінімальний клієнт до Telemetry API на стандартній бібліотеці.

Працює з endpoints, які реалізує `solution/main.py`:
`POST /telemetry` і `GET /telemetry/{drone_id}`. Зовнішні залежності
(requests/httpx) не потрібні — тільки stdlib.

Запуск (сервіс має слухати localhost:8000):

    python telemetry_client.py
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request

BASE_URL = 'http://localhost:8000'
MEASUREMENT = {
    'drone_id': '001',
    'lat': 50.45,
    'lon': 30.52,
    'alt': 100.0,
    'battery': 87,
}


def post_telemetry(payload: dict) -> tuple[int, dict]:
    request = urllib.request.Request(
        f'{BASE_URL}/telemetry',
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST',
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            return response.status, json.loads(response.read())
    except urllib.error.HTTPError as error:
        return error.code, json.loads(error.read())


def main() -> None:
    status, body = post_telemetry(MEASUREMENT)
    print(f'POST /telemetry -> {status}: {body}')

    status, body = post_telemetry(dict(MEASUREMENT, battery=150))
    print(f'POST /telemetry battery=150 -> {status}: {body}')

    with urllib.request.urlopen(f'{BASE_URL}/telemetry/001', timeout=5) as response:
        print(f'GET /telemetry/001 -> {response.status}: {json.loads(response.read())}')


if __name__ == '__main__':
    main()
