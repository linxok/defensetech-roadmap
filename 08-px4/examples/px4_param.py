import argparse
import asyncio
from mavsdk import System

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--get')
    parser.add_argument('--set')
    parser.add_argument('--value', type=float)
    args = parser.parse_args()

    drone = System()
    await drone.connect(system_address='udp://:14540')
    print('Connected to PX4')

    if args.get:
        value = await drone.param.get_param_float(args.get)
        print(f'{args.get} = {value}')
    elif args.set and args.value is not None:
        await drone.param.set_param_float(args.set, args.value)
        print(f'Set {args.set} = {args.value}')

asyncio.run(main())
