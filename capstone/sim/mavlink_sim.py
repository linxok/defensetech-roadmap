"""MAVLink-симулятор для capstone: потік, схожий на ArduPilot SITL.

Навмисно не залежить від автопілота: генерує HEARTBEAT,
GLOBAL_POSITION_INT, ATTITUDE, SYS_STATUS, BATTERY_STATUS і VFR_HUD,
щоб `docker compose up` показував живу телеметрію без зовнішніх образів.

Запуск:

    python mavlink_sim.py --target udpout:127.0.0.1:14550 --rate 5
    python mavlink_sim.py --target udpout:gateway:14550 --duration 60
"""

from __future__ import annotations

import argparse
import math
import time

from pymavlink import mavutil

BASE_LAT = 50.4501
BASE_LON = 30.5234
BASE_ALT = 120.0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', default='udpout:127.0.0.1:14550')
    parser.add_argument('--rate', type=float, default=5.0, help='кадрів за секунду')
    parser.add_argument('--duration', type=float, default=0.0, help='0 = безкінечно')
    parser.add_argument('--battery', type=int, default=87)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.rate <= 0:
        raise SystemExit('--rate must be > 0')

    master = mavutil.mavlink_connection(args.target, source_system=1)
    interval = 1.0 / args.rate
    started = time.monotonic()
    frame = 0

    while args.duration <= 0 or (time.monotonic() - started) < args.duration:
        t = time.monotonic() - started
        lat = BASE_LAT + 0.0005 * math.sin(t / 20)
        lon = BASE_LON + 0.0005 * math.cos(t / 20)
        alt = BASE_ALT + 5.0 * math.sin(t / 5)
        heading = int((math.degrees(t / 20) + 180) % 360)
        battery = max(5, args.battery - int(t / 60))

        master.mav.heartbeat_send(
            mavutil.mavlink.MAV_TYPE_QUADROTOR,
            mavutil.mavlink.MAV_AUTOPILOT_ARDUPILOTMEGA,
            81,  # base_mode: custom mode enabled + auto armed
            4,   # custom_mode: GUIDED
            mavutil.mavlink.MAV_STATE_ACTIVE,
        )
        master.mav.global_position_int_send(
            int(t * 1000),
            int(lat * 1e7),
            int(lon * 1e7),
            int(alt * 1000),
            int((alt - BASE_ALT + 100) * 1000),
            0, 0, 0,
            heading * 100,
        )
        master.mav.attitude_send(
            int(t * 1000), 0.0, 0.02 * math.sin(t), math.radians(heading), 0.0, 0.0, 0.0
        )
        master.mav.sys_status_send(
            0, 0, 0, 250, int(12.4 * 1000), -1, battery,
            0, 0, 0, 0, 0, 0,
        )
        master.mav.battery_status_send(
            0, 0, 0, 250, [12400] + [65535] * 9, -1, 0, 0, battery
        )
        master.mav.vfr_hud_send(
            0.0, 5.0 + 2.0 * math.sin(t / 10), heading, 55, alt, 0.5 * math.cos(t / 5)
        )

        frame += 1
        if frame % int(args.rate * 10) == 0:
            print(f'sim: {frame} frames, lat={lat:.5f} lon={lon:.5f} alt={alt:.1f}')
        time.sleep(interval)

    master.close()
    print(f'sim finished: {frame} frames')


if __name__ == '__main__':
    main()
