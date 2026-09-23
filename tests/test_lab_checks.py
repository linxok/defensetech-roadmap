"""Критерій якості перевірок: check падає на stub і проходить на solution/."""

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


def run_check(module: Path, target: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(module / 'checks' / 'check_lab.py'), '--target', str(target)],
        capture_output=True,
        text=True,
        timeout=300,
        check=False,
    )


@pytest.mark.parametrize('module', MODULES, ids=lambda path: path.name)
def test_check_passes_on_solution(module: Path):
    result = run_check(module, module / 'solution')
    assert result.returncode == 0, f'{module.name} check failed:\n{result.stdout}\n{result.stderr}'


def make_structured_stub(solution: Path, stub: Path) -> None:
    """Копія структури solution з порожнім вмістом файлів.

    Порожня тека — занадто слабкий stub: перевірка мала б падати й на
    «структурній заглушці», коли файли створені, але нічого не роблять.
    """
    for path in solution.rglob('*'):
        relative = path.relative_to(solution)
        destination = stub / relative
        if path.is_dir():
            destination.mkdir(parents=True, exist_ok=True)
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix == '.py':
            destination.write_text('pass\n', encoding='utf-8')
        elif path.suffix == '.json':
            destination.write_text('{}\n', encoding='utf-8')
        elif path.suffix in {'.yml', '.yaml'}:
            destination.write_text('services: {}\n', encoding='utf-8')
        elif path.suffix in {'.sh', '.rules', '.service'}:
            destination.write_text('#!/bin/sh\n', encoding='utf-8')
        else:
            destination.write_text('', encoding='utf-8')


@pytest.mark.parametrize('module', MODULES, ids=lambda path: path.name)
def test_check_fails_on_stub(module: Path, tmp_path: Path):
    result = run_check(module, tmp_path)
    assert result.returncode != 0, f'{module.name} check passed on an empty stub'


@pytest.mark.parametrize('module', MODULES, ids=lambda path: path.name)
def test_check_fails_on_structured_stub(module: Path, tmp_path: Path):
    stub = tmp_path / 'stub'
    stub.mkdir()
    make_structured_stub(module / 'solution', stub)
    result = run_check(module, stub)
    assert result.returncode != 0, (
        f'{module.name} check passed on a structured stub — перевірка нічого не міряє:\n'
        f'{result.stdout}'
    )
