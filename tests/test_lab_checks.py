"""Критерій Фази B: checks/ падає на stub і проходить на solution/."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

BASE = Path(__file__).resolve().parent.parent


def modules_with_checks() -> list[Path]:
    return sorted(
        path
        for path in BASE.iterdir()
        if path.is_dir()
        and path.name[:2].isdigit()
        and path.name[2] == '-'
        and (path / 'checks' / 'check_lab.py').is_file()
    )


MODULES = modules_with_checks()


def test_every_module_has_automatic_check():
    assert len(MODULES) == 18, f'checks missing for modules: {[m.name for m in MODULES]}'


@pytest.mark.parametrize('module', MODULES, ids=lambda path: path.name)
def test_check_passes_on_solution(module: Path):
    result = subprocess.run(
        [sys.executable, str(module / 'checks' / 'check_lab.py'), '--target', str(module / 'solution')],
        capture_output=True,
        text=True,
        timeout=300,
        check=False,
    )
    assert result.returncode == 0, f'{module.name} check failed:\n{result.stdout}\n{result.stderr}'


@pytest.mark.parametrize('module', MODULES, ids=lambda path: path.name)
def test_check_fails_on_stub(module: Path, tmp_path: Path):
    result = subprocess.run(
        [sys.executable, str(module / 'checks' / 'check_lab.py'), '--target', str(tmp_path)],
        capture_output=True,
        text=True,
        timeout=300,
        check=False,
    )
    assert result.returncode != 0, f'{module.name} check passed on an empty stub'
