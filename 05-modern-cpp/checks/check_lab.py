#!/usr/bin/env python3
"""Перевірка лабораторної 05: thread pool і MAVLink-парсер на C++.

Компілює та запускає еталонні програми g++ (без CMake, щоб працювати
в CI без додаткових інструментів):
- `thread_pool.cpp` має завершитися кодом 0 і вивести коректну суму;
- `parser_test.cpp` + `parser.cpp` — пройти known-answer тест CRC.

Запуск:
    python checks/check_lab.py --target solution
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODULE = HERE.parent
CXX = shutil.which('g++') or shutil.which('clang++')


def fail(message: str) -> None:
    print(f'FAIL: {message}')
    raise SystemExit(1)


def compile_and_run(sources: list[Path], output: Path, flags: list[str]) -> subprocess.CompletedProcess:
    command = [CXX, '-std=c++20', '-Wall', '-Wextra', '-Werror', *flags,
               *[str(s) for s in sources], '-o', str(output)]
    build = subprocess.run(command, capture_output=True, text=True, timeout=180, check=False)
    if build.returncode != 0:
        fail(f'компіляція не вдалася: {build.stderr[:500]}')
    return subprocess.run([str(output)], capture_output=True, text=True, timeout=60, check=False)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', type=Path, default=MODULE / 'solution')
    args = parser.parse_args()

    if CXX is None:
        fail('не знайдено g++/clang++ — встановіть компілятор C++')

    target = args.target
    thread_pool = target / 'thread_pool.cpp'
    parser_cpp = target / 'parser.cpp'
    parser_test = target / 'parser_test.cpp'
    parser_hpp = target / 'parser.hpp'
    for path in (thread_pool, parser_cpp, parser_test, parser_hpp):
        if not path.is_file():
            fail(f'{path} не існує')

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        pool_result = compile_and_run([thread_pool], tmp_path / 'thread_pool', ['-pthread'])
        if pool_result.returncode != 0:
            fail(f'thread_pool завершився з кодом {pool_result.returncode}: {pool_result.stdout}')
        if 'sum_of_squares=204' not in pool_result.stdout:
            fail(f'thread_pool не порахував задачі: {pool_result.stdout!r}')

        parser_result = compile_and_run(
            [parser_test, parser_cpp], tmp_path / 'parser_test', ['-I', str(target)]
        )
        if parser_result.returncode != 0:
            fail(f'parser_test провалився (код {parser_result.returncode}): '
                 f'{parser_result.stdout}{parser_result.stderr}')

    print('PASS: thread pool виконує чергу задач, парсер проходить CRC-тест')
    return 0


if __name__ == '__main__':
    sys.exit(main())
