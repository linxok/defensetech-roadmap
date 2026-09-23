"""Спрощений telemetry pipeline: HTTP → RabbitMQ.

Запуск (потрібен RabbitMQ на localhost:5672):

    pip install -r requirements.txt
    RABBITMQ_URL=amqp://guest:guest@localhost:5672/ uvicorn telemetry_pipeline:app --reload

З'єднання створюється у lifespan, а не при імпорті; синхронний pika
виконується через asyncio.to_thread. Повний еталон — `solution/main.py`.
"""

from __future__ import annotations

import asyncio
import json
import os
from contextlib import asynccontextmanager
from typing import Any

import pika
from fastapi import FastAPI

RABBITMQ_URL = os.environ.get('RABBITMQ_URL', 'amqp://guest:guest@localhost:5672/')
QUEUE = 'telemetry'


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
        await asyncio.wait_for(
            asyncio.to_thread(
                self._channel.basic_publish,
                exchange='',
                routing_key=QUEUE,
                body=body,
                properties=pika.BasicProperties(delivery_mode=2),
            ),
            timeout=10,
        )

    async def close(self) -> None:
        if self._connection is not None:
            await asyncio.to_thread(self._connection.close)
            self._connection = None
            self._channel = None


def create_app(publisher: RabbitPublisher | None = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.publisher = publisher or RabbitPublisher(RABBITMQ_URL)
        await app.state.publisher.connect()
        try:
            yield
        finally:
            await app.state.publisher.close()

    app = FastAPI(title='Telemetry Pipeline (example)', lifespan=lifespan)

    @app.post('/telemetry', status_code=202)
    async def receive(data: dict) -> dict[str, str]:
        await app.state.publisher.publish(json.dumps(data).encode())
        return {'status': 'queued'}

    @app.get('/health')
    async def health() -> dict[str, str]:
        return {'status': 'ok'}

    return app


app = create_app()

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=8000)
