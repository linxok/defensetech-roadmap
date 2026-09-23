"""CLI для читання/запису параметрів PX4 через MAVSDK.

Запуск:

    python px4_param.py get MPC_XY_VEL_MAX
    python px4_param.py set MPC_XY_VEL_MAX 12.5
    python px4_param.py list MPC_XY

Передумова: PX4 SITL (`make px4_sitl gz_x500`) на udp://:14540.
"""

from __future__ import annotations

import argparse
import asyncio
import re
import sys
from typing import Any, Iterable, Sequence

from mavsdk import System

PARAM_RE = re.compile(r'^[A-Z][A-Z0-9_]{0,15}$')
CONNECT_TIMEOUT = 30.0


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='PX4 parameter manager')
    sub = parser.add_subparsers(dest='command', required=True)

    get = sub.add_parser('get', help='read one parameter')
    get.add_argument('name')

    set_ = sub.add_parser('set', help='write one parameter')
    set_.add_argument('name')
    set_.add_argument('value', type=float)

    list_ = sub.add_parser('list', help='list parameters by prefix')
    list_.add_argument('prefix', nargs='?', default='')
    return parser.parse_args(argv)


def validate_name(name: str) -> str:
    if not PARAM_RE.match(name):
        raise SystemExit(f'invalid PX4 parameter name: {name!r}')
    return name


def format_param(name: str, value: float) -> str:
    return f'{validate_name(name)} = {value:.6g}'


def format_params(params: Iterable[Any]) -> list[str]:
    return [
        f'{param.name} = {param.value:.6g}'
        for param in sorted(params, key=lambda item: item.name)
    ]


async def connect(address: str) -> System:
    drone = System()
    await drone.connect(system_address=address)
    async for state in drone.core.connection_state():
        if state.is_connected:
            return drone
    raise TimeoutError(f'no PX4 connection at {address}')


async def run(args: argparse.Namespace, address: str) -> int:
    drone = await asyncio.wait_for(connect(address), timeout=CONNECT_TIMEOUT)

    if args.command == 'get':
        value = await asyncio.wait_for(
            drone.param.get_param_float(validate_name(args.name)), timeout=10
        )
        print(format_param(args.name, value))
    elif args.command == 'set':
        await asyncio.wait_for(
            drone.param.set_param_float(validate_name(args.name), args.value),
            timeout=10,
        )
        print(f'{args.name} := {args.value}')
    elif args.command == 'list':
        prefix = validate_name(args.prefix) if args.prefix else ''
        async for param in drone.param.get_all_params():
            if str(param.name).startswith(prefix):
                print(format_param(str(param.name), float(param.value)))
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    address = 'udp://:14540'
    try:
        return asyncio.run(run(args, address))
    except TimeoutError as exc:
        print(f'timeout: {exc}', file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 130


if __name__ == '__main__':
    raise SystemExit(main())
