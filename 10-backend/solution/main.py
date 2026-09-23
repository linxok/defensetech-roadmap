"""Telemetry pipeline: HTTP → RabbitMQ без блокування event loop.

Запуск:

    RABBITMQ_URL=amqp://guest:guest@localhost:5672/ \
        uvicorn telemetry_pipeline:app --reload

Важливо: з'єднання з брокером створюється у lifespan, а не при імпорті.
Синхронний pika виконується через asyncio.to_thread.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Protocol

import pika
from fastapi import FastAPI, HTTPException

log = logging.getLogger('telemetry_pipeline')

RABBITMQ_URL = os.environ.get('RABBITMQ_URL', 'amqp://guest:guest@localhost:5672/')
QUEUE = 'telemetry'


class Publisher(Protocol):
    async def publish(self, body: bytes) -> None: ...

    async def close(self) -> None: ...


class RabbitPublisher:
    def __init__(self, url: str) -> None:
        self._url = url
        self._connection: pika.BlockingConnection | None = None
        self._channel: Any = None

    async def connect(self) -> None:
        params = pika.URLParameters(self._url)
        params.blocked_connection_timeout = 10
        self._connection = await asyncio.wait_for(
            asyncio.to_thread(pika.BlockingConnection, params), timeout=10
        )
        self._channel = await asyncio.to_thread(self._connection.channel)
        await asyncio.to_thread(
            self._channel.queue_declare, queue=QUEUE, durable=True
        )

    async def publish(self, body: bytes) -> None:
        if self._channel is None:
            raise RuntimeError('publisher is not connected')
        await asyncio.to_thread(
            self._channel.basic_publish,
            exchange='',
            routing_key=QUEUE,
            body=body,
            properties=pika.BasicProperties(delivery_mode=2),
        )

    async def close(self) -> None:
        if self._connection is not None:
            await asyncio.to_thread(self._connection.close)
            self._connection = None
            self._channel = None


def create_app(publisher: Publisher | None = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        app.state.publisher = publisher or RabbitPublisher(RABBITMQ_URL)
        await app.state.publisher.connect()
        try:
            yield
        finally:
            await app.state.publisher.close()

    app = FastAPI(title='Telemetry Pipeline', lifespan=lifespan)

    @app.post('/telemetry', status_code=202)
    async def receive(data: dict) -> dict[str, str]:
        try:
            body = json.dumps(data).encode()
        except (TypeError, ValueError) as exc:
            raise HTTPException(status_code=422, detail=f'invalid payload: {exc}') from exc
        await app.state.publisher.publish(body)
        return {'status': 'queued'}

    @app.get('/health')
    async def health() -> dict[str, str]:
        return {'status': 'ok'}

    return app


app = create_app()

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=8000)
