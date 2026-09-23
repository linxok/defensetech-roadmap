"""Перевірки якості контенту: контракт lab ↔ checks, приклади ≠ розв'язки, статуси.

Ці тести захищають від регресій, знайдених аудитом:
- lab.md мусить згадувати контракт, який вимагає checks/check_lab.py,
  інакше студент, який виконав лабораторну, не проходить перевірку;
- examples/ не можуть бути побайтовими копіями solution/;
- таблиця статусів у кореневому README мусить збігатися з модульними.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

BASE = Path(__file__).resolve().parent.parent

LAB_CHECK_CONTRACT = {
    '02-linux-for-robotics': ('Restart=on-failure', 'After=network-online.target'),
    '03-networking': ('parse_packet', 'TelemetryHub', 'UdpTelemetryProtocol'),
    '04-python': ('Field(', '422'),
    '05-modern-cpp': ('sum_of_squares', 'crc'),
    '06-mavlink': ('mavlink_to_telemetry', 'TelemetryHub', 'to_thread'),
    '07-ardupilot': ('create_app', 'ardupilot_api.py'),
    '08-px4': ('validate_name', 'format_param', 'format_params'),
    '09-ros2': ('bridge_logic.py', 'mavlink_to_dict', 'destroy_node'),
    '10-backend': ('create_app', 'CREATE TABLE'),
    '11-distributed-systems': ('StreamTelemetry', 'GetLast', 'DroneRequest'),
    '12-computer-vision': ('letterbox', 'postprocess', 'scale_to_frame'),
    '13-ai': ('Waypoint', 'Mission', 'offline_mission'),
    '14-ground-control': ('telemetry-format.mjs', 'NEXT_PUBLIC_WS_URL'),
    '15-devops': ('Dockerfile', 'docker-compose.yml', 'k8s-deployment.yaml'),
}


def module_dirs() -> list[Path]:
    return sorted(
        path
        for path in BASE.iterdir()
        if path.is_dir() and len(path.name) > 2 and path.name[:2].isdigit() and path.name[2] == '-'
    )


@pytest.mark.parametrize('module', LAB_CHECK_CONTRACT, ids=str)
def test_lab_defines_check_contract(module: str):
    lab = (BASE / module / 'lab.md').read_text(encoding='utf-8').lower()
    missing = [token for token in LAB_CHECK_CONTRACT[module] if token.lower() not in lab]
    assert not missing, f'{module}/lab.md не згадує контракт check: {missing}'


def test_examples_are_not_copies_of_solutions():
    copied: list[str] = []
    for module in module_dirs():
        examples = module / 'examples'
        solution = module / 'solution'
        if not examples.is_dir() or not solution.is_dir():
            continue
        solution_blobs: dict[bytes, str] = {
            path.read_bytes(): str(path.relative_to(BASE))
            for path in solution.rglob('*')
            if path.is_file() and path.suffix in {'.py', '.cpp', '.hpp', '.mjs', '.tsx', '.proto'}
        }
        for path in examples.rglob('*'):
            if not path.is_file():
                continue
            blob = path.read_bytes()
            if blob in solution_blobs:
                copied.append(f'{path.relative_to(BASE)} == {solution_blobs[blob]}')
    assert not copied, 'examples/ копіюють solution/:\n' + '\n'.join(copied)


def test_root_status_table_matches_module_readmes():
    root = (BASE / 'README.md').read_text(encoding='utf-8')
    rows = re.findall(r'^\|\s*(\d\d)\s+[^|]+\|\s*(stub|outline|complete)\s*\|', root, flags=re.MULTILINE)
    assert len(rows) == 18, f'у таблиці статусів кореневого README не 18 модулів: {len(rows)}'
    mismatches: list[str] = []
    for number, status in rows:
        module = next(path for path in module_dirs() if path.name.startswith(number))
        module_readme = (module / 'README.md').read_text(encoding='utf-8')
        match = re.search(r'>\s*Статус:\s*(stub|outline|complete)', module_readme)
        if match is None or match.group(1) != status:
            mismatches.append(f'{module.name}: README={status}, module={match.group(1) if match else "none"}')
    assert not mismatches, 'Статуси розійшлися:\n' + '\n'.join(mismatches)
