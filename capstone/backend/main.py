"""Backend: HTTP → RabbitMQ + WebSocket live feed.

Ключові вимоги:
- жодних з'єднань на етапі імпорту (усе в lifespan);
- синхронний pika виконується через asyncio.to_thread;
- список WebSocket-клієнтів захищений asyncio.Lock;
- збій одного клієнта не зриває розсилку іншим.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Protocol

import pika
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect

log = logging.getLogger('backend')
logging.basicConfig(level=logging.INFO)

RABBITMQ_URL = os.environ.get('RABBITMQ_URL', 'amqp://guest:guest@rabbitmq:5672/')
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
            asyncio.to_thread(pika.BlockingConnection, params), timeout=15
        )
        self._channel = await asyncio.to_thread(self._connection.channel)
        await asyncio.to_thread(self._channel.queue_declare, queue=QUEUE, durable=True)

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


class ConnectionManager:
    def __init__(self) -> None:
        self._clients: set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._clients.add(websocket)

    async def disconnect(self, websocket: WebSocket) -> None:
        async with self._lock:
            self._clients.discard(websocket)

    async def broadcast(self, message: str) -> None:
        async with self._lock:
            clients = list(self._clients)
        if not clients:
            return
        results = await asyncio.gather(
            *(client.send_text(message) for client in clients), return_exceptions=True
        )
        for client, result in zip(clients, results):
            if isinstance(result, Exception):
                log.warning('dropping websocket client: %s', result)
                await self.disconnect(client)

    @property
    def count(self) -> int:
        return len(self._clients)


def create_app(publisher: Publisher | None = None) -> FastAPI:
    manager = ConnectionManager()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        app.state.publisher = publisher or RabbitPublisher(RABBITMQ_URL)
        await app.state.publisher.connect()
        try:
            yield
        finally:
            await app.state.publisher.close()

    app = FastAPI(title='Capstone Telemetry Backend', lifespan=lifespan)
    app.state.manager = manager

    @app.post('/telemetry', status_code=202)
    async def receive(payload: dict) -> dict[str, str]:
        if 'type' not in payload:
            raise HTTPException(status_code=422, detail='field "type" is required')
        body = json.dumps(payload, ensure_ascii=False).encode()
        await app.state.publisher.publish(body)
        await manager.broadcast(json.dumps(payload, ensure_ascii=False))
        return {'status': 'accepted'}

    @app.websocket('/ws')
    async def websocket_endpoint(websocket: WebSocket) -> None:
        await manager.connect(websocket)
        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            await manager.disconnect(websocket)

    @app.get('/health')
    async def health() -> dict[str, Any]:
        return {'status': 'ok', 'ws_clients': manager.count}

    return app


app = create_app()
