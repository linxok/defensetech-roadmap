#!/usr/bin/env python3
"""Перевірка лабораторної 11: gRPC-контракт.

Контракт (див. lab.md): `telemetry.proto` зі service Telemetry,
client-streaming RPC StreamTelemetry, unary RPC GetLast і
повідомленнями TelemetryFrame/Ack із заданими полями та тегами.
Перевірка структурна: компіляція protoc — окремий крок у README.

Запуск:
    python checks/check_lab.py --target solution
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODULE = HERE.parent

EXPECTED_FIELDS = {
    'TelemetryFrame': {
        'drone_id': ('string', 1),
        'timestamp_ms': ('int64', 2),
        'lat': ('double', 3),
        'lon': ('double', 4),
        'alt': ('double', 5),
        'battery': ('int32', 6),
    },
    'Ack': {
        'accepted': ('bool', 1),
        'received': ('int32', 2),
    },
}


def fail(message: str) -> None:
    print(f'FAIL: {message}')
    raise SystemExit(1)


def message_body(text: str, name: str) -> str:
    match = re.search(rf'message\s+{name}\s*\{{(.*?)\}}', text, re.DOTALL)
    if match is None:
        fail(f'немає повідомлення {name}')
    return match.group(1)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', type=Path, default=MODULE / 'solution')
    args = parser.parse_args()

    path = args.target / 'telemetry.proto'
    if not path.is_file():
        fail(f'{path} не існує')

    text = path.read_text(encoding='utf-8')
    if 'syntax = "proto3";' not in text:
        fail('proto має бути proto3')
    if not re.search(r'package\s+\w+(\.\w+)*\s*;', text):
        fail('немає package')

    if 'service Telemetry' not in text:
        fail('немає `service Telemetry`')
    if not re.search(r'rpc\s+StreamTelemetry\s*\(\s*stream\s+TelemetryFrame\s*\)\s*returns\s*\(\s*Ack\s*\)', text):
        fail('StreamTelemetry має бути client-streaming RPC, що повертає Ack')
    if not re.search(r'rpc\s+GetLast\s*\(\s*DroneRequest\s*\)\s*returns\s*\(\s*TelemetryFrame\s*\)', text):
        fail('GetLast має бути unary RPC DroneRequest → TelemetryFrame')

    for message, fields in EXPECTED_FIELDS.items():
        body = message_body(text, message)
        for field, (field_type, tag) in fields.items():
            pattern = rf'\b{field_type}\s+{field}\s*=\s*{tag}\s*;'
            if not re.search(pattern, body):
                fail(f'{message}.{field} має бути `{field_type} {field} = {tag};`')

    for message in EXPECTED_FIELDS:
        body = message_body(text, message)
        tags = re.findall(r'=\s*(\d+)\s*;', body)
        if len(tags) != len(set(tags)):
            fail(f'у {message} теги полів повторюються')

    print('PASS: proto містить сервіс, обидва RPC і коректні поля з тегами')
    return 0


if __name__ == '__main__':
    sys.exit(main())
