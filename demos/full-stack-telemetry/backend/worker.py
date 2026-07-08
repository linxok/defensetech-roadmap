import json
import os
import pika
import psycopg2
from datetime import datetime

DSN = os.environ.get('DATABASE_URL', 'postgresql://drone:secret@postgres:5432/drone')
connection = pika.BlockingConnection(pika.URLParameters('amqp://guest:guest@rabbitmq:5672/'))
channel = connection.channel()
channel.queue_declare(queue='telemetry')

def callback(ch, method, properties, body):
    data = json.loads(body)
    with psycopg2.connect(DSN) as conn:
        with conn.cursor() as cur:
            cur.execute('''
                CREATE TABLE IF NOT EXISTS telemetry (
                    id BIGSERIAL PRIMARY KEY,
                    drone_id TEXT,
                    ts TIMESTAMP,
                    lat DOUBLE PRECISION,
                    lon DOUBLE PRECISION,
                    alt DOUBLE PRECISION,
                    battery INT
                )
            ''')
            cur.execute('''
                INSERT INTO telemetry (drone_id, ts, lat, lon, alt, battery)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (data['drone_id'], datetime.utcnow(), data.get('lat'), data.get('lon'), data.get('alt'), data.get('battery')))
        conn.commit()
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_qos(prefetch_count=10)
channel.basic_consume(queue='telemetry', on_message_callback=callback)
print('Worker started')
channel.start_consuming()
