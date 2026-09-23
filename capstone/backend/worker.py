"""Worker: RabbitMQ → PostgreSQL.

З'єднання створюються лише всередині `consume_once`, тому імпорт
модуля безпечний. При недоступності брокера/БД — ретрай із затримкою.
"""

from __future__ import annotations

import json
import logging
import os
import time
from datetime import datetime, timezone

import pika
import psycopg2

log = logging.getLogger('capstone.worker')
logging.basicConfig(level=logging.INFO)

DSN = os.environ.get('DATABASE_URL', 'postgresql://drone:secret@postgres:5432/drone')
BROKER_URL = os.environ.get('RABBITMQ_URL', 'amqp://guest:guest@rabbitmq:5672/')
QUEUE = 'telemetry'

DDL = """
CREATE TABLE IF NOT EXISTS telemetry (
    id BIGSERIAL PRIMARY KEY,
    type TEXT,
    system_id INT,
    ts TIMESTAMPTZ NOT NULL,
    lat DOUBLE PRECISION,
    lon DOUBLE PRECISION,
    alt DOUBLE PRECISION,
    battery INT
)
"""

INSERT = """
INSERT INTO telemetry (type, system_id, ts, lat, lon, alt, battery)
VALUES (%s, %s, %s, %s, %s, %s, %s)
"""


def store(data: dict) -> None:
    ts = data.get('ts') or datetime.now(timezone.utc).isoformat()
    with psycopg2.connect(DSN, connect_timeout=5) as connection:
        with connection.cursor() as cursor:
            cursor.execute(DDL)
            cursor.execute(
                INSERT,
                (
                    data.get('type'),
                    data.get('system_id'),
                    ts,
                    data.get('lat'),
                    data.get('lon'),
                    data.get('alt'),
                    data.get('battery'),
                ),
            )


def on_message(channel, method, properties, body) -> None:
    try:
        store(json.loads(body))
    except (json.JSONDecodeError, KeyError) as exc:
        log.warning('rejecting malformed message: %s', exc)
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        return
    channel.basic_ack(delivery_tag=method.delivery_tag)


def consume_once() -> None:
    with pika.BlockingConnection(pika.URLParameters(BROKER_URL)) as connection:
        channel = connection.channel()
        channel.queue_declare(queue=QUEUE, durable=True)
        channel.basic_qos(prefetch_count=10)
        channel.basic_consume(queue=QUEUE, on_message_callback=on_message)
        log.info('worker started, waiting for telemetry')
        channel.start_consuming()


def main() -> None:
    while True:
        try:
            consume_once()
        except (pika.exceptions.AMQPConnectionError, psycopg2.OperationalError) as exc:
            log.error('broker/db unavailable (%s), retrying in 5s', exc)
            time.sleep(5)


if __name__ == '__main__':
    main()
