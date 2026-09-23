"""FastAPI-застосунок для прикладів DevOps: мінімальний сервіс із `/health`.

Запуск:

    uvicorn main:app --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

from fastapi import FastAPI

app = FastAPI(title='Telemetry API Example')


@app.get('/health')
async def health() -> dict[str, str]:
    return {'status': 'ok'}
