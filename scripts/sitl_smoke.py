#!/usr/bin/env python3
"""SITL smoke-test: підключитися до MAVLink і дочекатися heartbeat.

Використовується в нічному CI-job і локально:

    python3 scripts/sitl_smoke.py --source udp:127.0.0.1:14550 --timeout 90

Успіх: отримано HEARTBEAT і хоча б один GLOBAL_POSITION_INT.
"""

from __future__ import annotations

import argparse
import sys
import time

from pymavlink import mavutil


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', default='udp:127.0.0.1:14550')
    parser.add_argument('--timeout', type=float, default=90.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    started = time.monotonic()
    print(f'connecting to {args.source} (timeout {args.timeout:.0f}s)')

    connection = mavutil.mavlink_connection(args.source, source_system=255)
    heartbeat = connection.wait_heartbeat(timeout=args.timeout)
    if heartbeat is None:
        print('FAIL: no HEARTBEAT', file=sys.stderr)
        return 1

    print(
        f'heartbeat: system={connection.target_system} '
        f'component={connection.target_component} type={heartbeat.type} '
        f'autopilot={heartbeat.autopilot} status={heartbeat.system_status}'
    )

    remaining = max(5.0, args.timeout - (time.monotonic() - started))
    position = connection.recv_match(
        type='GLOBAL_POSITION_INT', blocking=True, timeout=remaining
    )
    if position is None:
        print('FAIL: no GLOBAL_POSITION_INT', file=sys.stderr)
        return 1

    print(
        f'position: lat={position.lat / 1e7:.6f} lon={position.lon / 1e7:.6f} '
        f'alt={position.alt / 1000.0:.1f} m'
    )
    print('SITL smoke test passed.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
