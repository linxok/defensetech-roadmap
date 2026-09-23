"""Звіт по ULog: теми, кількість семплів, часовий діапазон.

Запуск:

    python ulog_summary.py log.ulg [--topics ATTITUDE,GPS]

pyulog не потребує SITL — читає вже записаний лог.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pyulog import ULog


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('log', type=Path)
    parser.add_argument(
        '--topics',
        default='',
        help='через кому: показати поля лише цих топіків',
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.log.is_file():
        print(f'file not found: {args.log}', file=sys.stderr)
        return 1

    try:
        log = ULog(str(args.log))
    except Exception as exc:  # pyulog кидає різні типи на битих файлах
        print(f'cannot read ULog: {exc}', file=sys.stderr)
        return 1

    wanted = {t.strip() for t in args.topics.split(',') if t.strip()}
    duration = (log.last_timestamp - log.start_timestamp) / 1e6
    print(f'log: {args.log} ({duration:.1f} s of logged data)')
    print(f'topics: {len(log.data_list)}')
    for data in sorted(log.data_list, key=lambda d: d.name):
        if wanted and data.name not in wanted:
            continue
        fields = ', '.join(data.field_data.keys())
        samples = max((len(column) for column in data.data.values()), default=0)
        print(f'  {data.name}: {samples} samples [{fields}]')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
