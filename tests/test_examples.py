"""Smoke-перевірки прикладів: імпорт без мережі та `--help` CLI."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

BASE = Path(__file__).resolve().parent.parent

IMPORT_SMOKE = (
    ('04-python/examples/fastapi_telemetry.py', ('app',)),
    ('04-python/examples/telemetry_client.py', ('post_telemetry',)),
    ('10-backend/examples/telemetry_pipeline.py', ('app', 'create_app')),
    ('10-backend/examples/telemetry_worker.py', ('store', 'on_message', 'main')),
    ('06-mavlink/examples/mavlink_gateway.py', ('mavlink_to_telemetry', 'TelemetryHub')),
    ('07-ardupilot/examples/ardupilot_api.py', ('app', 'create_app')),
    ('08-px4/examples/ulog_summary.py', ('main',)),
    ('12-computer-vision/examples/yolo_opencv.py', ('postprocess', 'letterbox')),
    ('12-computer-vision/examples/track_objects.py', ('main',)),
    ('13-ai/examples/mission_prompt.py', ('Mission', 'offline_mission')),
    ('13-ai/examples/rag_simple.py', ('retrieve',)),
    ('15-devops/examples/main.py', ('app',)),
    ('capstone/backend/main.py', ('app', 'create_app')),
    ('capstone/backend/worker.py', ('store', 'on_message')),
    ('capstone/gateway/gateway.py', ('mavlink_to_telemetry',)),
    ('capstone/sim/mavlink_sim.py', ('main',)),
    ('09-ros2/solution/bridge_logic.py', ('mavlink_to_dict',)),
)

CLI_HELP = (
    '08-px4/examples/px4_param.py',
    '08-px4/examples/ulog_summary.py',
    '12-computer-vision/examples/yolo_opencv.py',
    '13-ai/examples/mission_prompt.py',
    'scripts/sitl_smoke.py',
)


def _load(path: Path):
    spec = importlib.util.spec_from_file_location(f'smoke_{path.stem}', path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize('relative,attributes', IMPORT_SMOKE)
def test_example_imports_without_side_effects(relative: str, attributes: tuple[str, ...]):
    path = BASE / relative
    assert path.is_file(), f'{relative} missing'
    module = _load(path)
    for attribute in attributes:
        assert hasattr(module, attribute), f'{relative} has no {attribute}'


@pytest.mark.parametrize('relative', CLI_HELP)
def test_cli_help_exits_zero(relative: str):
    result = subprocess.run(
        [sys.executable, str(BASE / relative), '--help'],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert result.returncode == 0, f'{relative} --help failed: {result.stderr[-300:]}'


def test_gateway_module_has_no_forbidden_asyncio_wait():
    source = (BASE / '06-mavlink/examples/mavlink_gateway.py').read_text(encoding='utf-8')
    assert 'asyncio.wait(' not in source
    assert 'asyncio.to_thread' in source


def test_capstone_backend_has_no_import_time_connection():
    source = (BASE / 'capstone/backend/main.py').read_text(encoding='utf-8')
    assert 'pika.BlockingConnection' in source  # лише в класі RabbitPublisher
    top_level = source.split('class ', 1)[0]
    assert 'pika.BlockingConnection' not in top_level
    assert 'lifespan' in source
