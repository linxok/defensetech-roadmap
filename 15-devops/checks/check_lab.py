#!/usr/bin/env python3
"""Перевірка лабораторної 15: Docker + Kubernetes.

Контракт (див. lab.md):
- `Dockerfile` — pinned base, non-root USER, HEALTHCHECK;
- `docker-compose.yml` — healthchecks для stateful-сервісів, без :latest;
- k8s Deployment — resources, probes, без :latest.

Запуск:
    python checks/check_lab.py --target solution
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
MODULE = HERE.parent

STATEFUL = {'db', 'postgres', 'postgresql', 'redis', 'cache', 'rabbitmq', 'kafka'}


def fail(message: str) -> None:
    print(f'FAIL: {message}')
    raise SystemExit(1)


def check_dockerfile(text: str) -> None:
    lines = [line.strip() for line in text.splitlines() if line.strip() and not line.strip().startswith('#')]
    from_lines = [line for line in lines if line.upper().startswith('FROM')]
    if not from_lines:
        fail('Dockerfile без FROM')
    base = from_lines[0].split()[1]
    if ':' not in base or base.endswith(':latest') or '@' not in base and not base.split(':')[1]:
        fail(f'базовий образ має бути pinned (не latest): {base}')
    user_lines = [line for line in lines if line.upper().startswith('USER ')]
    if not user_lines or user_lines[-1].split()[1] in ('root', '0'):
        fail('контейнер має працювати від непривілейованого USER')
    if not any(line.upper().startswith('HEALTHCHECK') for line in lines):
        fail('немає HEALTHCHECK')


def check_compose(document: dict) -> None:
    services = document.get('services') or {}
    if not services:
        fail('docker-compose.yml без services')
    for name, service in services.items():
        image = str(service.get('image', ''))
        if image.endswith(':latest'):
            fail(f'сервіс {name} використовує :latest — зафіксуйте тег')
        if name in STATEFUL and not service.get('healthcheck') and 'build' not in service:
            fail(f'stateful-сервіс {name} має мати healthcheck')


def check_k8s(document: dict) -> None:
    if document.get('kind') != 'Deployment':
        return
    spec = document.get('spec', {}).get('template', {}).get('spec', {})
    containers = spec.get('containers') or []
    if not containers:
        fail('Deployment без контейнерів')
    container = containers[0]
    image = str(container.get('image', ''))
    if not image or image.endswith(':latest'):
        fail(f'образ має бути pinned: {image!r}')
    if not container.get('resources', {}).get('requests') or not container.get('resources', {}).get('limits'):
        fail('контейнер має задавати resources.requests і limits')
    if not container.get('readinessProbe'):
        fail('немає readinessProbe')
    if not (spec.get('securityContext', {}).get('runAsNonRoot') or container.get('securityContext', {}).get('runAsNonRoot')):
        fail('немає runAsNonRoot')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', type=Path, default=MODULE / 'solution')
    args = parser.parse_args()

    dockerfile = args.target / 'Dockerfile'
    compose = args.target / 'docker-compose.yml'
    k8s = args.target / 'k8s-deployment.yaml'
    for path in (dockerfile, compose, k8s):
        if not path.is_file():
            fail(f'{path} не існує')

    check_dockerfile(dockerfile.read_text(encoding='utf-8'))

    compose_data = yaml.safe_load(compose.read_text(encoding='utf-8'))
    if not isinstance(compose_data, dict):
        fail('docker-compose.yml не є YAML-обʼєктом')
    check_compose(compose_data)

    deployments = 0
    for document in yaml.safe_load_all(k8s.read_text(encoding='utf-8')):
        if document and document.get('kind') == 'Deployment':
            deployments += 1
            check_k8s(document)
    if deployments == 0:
        fail('k8s-deployment.yaml без Deployment')

    print('PASS: Dockerfile, compose і k8s-манифест відповідають вимогам')
    return 0


if __name__ == '__main__':
    sys.exit(main())
