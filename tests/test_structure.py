"""Структурні перевірки репозиторію курсу."""

from __future__ import annotations

import os
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
EXCLUDE = {'.git', '.github', '.kilo', '.mkdocs-build', 'capstone', 'demos', 'docs',
           'node_modules', 'notes', 'scripts', 'site', 'tests', 'venv'}

MODULE_FILES = (
    'README.md',
    'detailed-guide.md',
    'lab.md',
    'practice.md',
    'homework.md',
    'checklist.md',
    'self-assessment.md',
    'faq.md',
    'interview-questions.md',
    'cheat-sheet.md',
    'resources.md',
    'templates.md',
    'mini-project.md',
    'project-ideas.md',
    'real-world-scenario.md',
)

REMOVED_FILES = ('further-reading.md',)


def modules() -> list[Path]:
    return sorted(
        path
        for path in BASE.iterdir()
        if path.is_dir() and len(path.name) > 2 and path.name[:2].isdigit() and path.name[2] == '-'
    )


def test_eighteen_modules_exist():
    assert [m.name for m in modules()] == [
        '00-introduction', '01-defense-fundamentals', '02-linux-for-robotics',
        '03-networking', '04-python', '05-modern-cpp', '06-mavlink', '07-ardupilot',
        '08-px4', '09-ros2', '10-backend', '11-distributed-systems',
        '12-computer-vision', '13-ai', '14-ground-control', '15-devops',
        '16-projects', '17-interview',
    ]


def test_root_files_exist():
    for name in (
        'README.md', 'LICENSE', 'CONTRIBUTING.md', 'ROADMAP.md', 'mkdocs.yml',
        'QUICKSTART.md', 'requirements.txt', 'requirements-dev.txt',
        'requirements-docs.txt', 'requirements-optional.txt',
        'CONTENT_STANDARD.md', 'STUDY_SCHEDULE.md',
        'CERTIFICATION_CHECKLIST.md',
    ):
        assert (BASE / name).is_file(), f'{name} not found'


def test_module_contract_files_exist():
    for module in modules():
        for name in MODULE_FILES:
            assert (module / name).is_file(), f'{module.name}/{name} missing'
        assert (module / 'examples').is_dir(), f'{module.name}/examples missing'
        assert (module / 'checks' / 'check_lab.py').is_file(), f'{module.name}/checks/check_lab.py missing'
        assert (module / 'solution').is_dir(), f'{module.name}/solution missing'


def test_module_readme_has_status():
    for module in modules():
        text = (module / 'README.md').read_text(encoding='utf-8')
        assert '> Статус:' in text, f'{module.name}/README.md has no status line'


def test_removed_template_files_are_gone():
    for module in modules():
        for name in REMOVED_FILES:
            assert not (module / name).exists(), f'{module.name}/{name} should be removed'


def test_shared_docs_exist():
    for name in ('learning-workflow.md', 'faq.md', 'templates.md'):
        assert (BASE / 'docs' / name).is_file(), f'docs/{name} missing'
