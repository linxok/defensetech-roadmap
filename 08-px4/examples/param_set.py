import asyncio
from mavsdk import System

async def main():
    drone = System()
    await drone.connect(system_address='udp://:14540')
    param = drone.param
    await param.set_param_float('MPC_XY_P', 0.8)
    print('Parameter updated')

asyncio.run(main())
