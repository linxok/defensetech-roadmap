"""Спрощений CLI параметрів PX4 через MAVSDK (приклад до модуля 08).

Команди ті самі, що в лабораторній, але розбір аргументів коротший:
замість підпарсерів — позиційні `command`, `name` і `value`. Еталон із
валідацією та форматуванням — `solution/px4_param.py`.

    python px4_param.py get MPC_XY_VEL_MAX
    python px4_param.py set MPC_XY_VEL_MAX 12.5
    python px4_param.py list MPC_XY

Передумова: PX4 SITL (`make px4_sitl gz_x500`) на udp://:14540.
"""

from __future__ import annotations

import argparse
import asyncio
import sys

from mavsdk import System

ADDRESS = 'udp://:14540'
COMMANDS = ('get', 'set', 'list')


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description='simple PX4 parameter CLI')
    parser.add_argument('command', choices=COMMANDS)
    parser.add_argument('name', nargs='?', default='')
    parser.add_argument('value', nargs='?', type=float)
    return parser.parse_args(argv)


async def get_drone():
    drone = System()
    await drone.connect(system_address=ADDRESS)
    async for state in drone.core.connection_state():
        if state.is_connected:
            break
    return drone


async def run(args) -> int:
    drone = await get_drone()
    if args.command == 'get' and args.name:
        value = await drone.param.get_param_float(args.name)
        print(f'{args.name} = {value:g}')
    elif args.command == 'set' and args.name and args.value is not None:
        await drone.param.set_param_float(args.name, args.value)
        print(f'{args.name} := {args.value}')
    else:
        async for param in drone.param.get_all_params():
            if str(param.name).startswith(args.name):
                print(f'{param.name} = {float(param.value):g}')
    return 0


def main(argv=None) -> int:
    args = parse_args(argv)
    try:
        return asyncio.run(asyncio.wait_for(run(args), timeout=30))
    except TimeoutError:
        print('timeout: no PX4 connection at ' + ADDRESS, file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 130


if __name__ == '__main__':
    raise SystemExit(main())
