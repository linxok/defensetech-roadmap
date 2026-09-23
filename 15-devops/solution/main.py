"""Мінімальний FastAPI-сервіс для лабораторної 15.

Ендпоінт `/health` використовують HEALTHCHECK у Dockerfile,
healthcheck у compose і probes у k8s-манифесті.

Запуск локально:

    uvicorn main:app --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

from fastapi import FastAPI

app = FastAPI(title='Telemetry API')


@app.get('/health')
async def health() -> dict[str, str]:
    return {'status': 'ok'}
