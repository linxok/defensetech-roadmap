import json
import pika
import psycopg2
from datetime import datetime

DB_DSN = 'dbname=drone user=postgres password=secret host=localhost'
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='telemetry')

def callback(ch, method, properties, body):
    data = json.loads(body)
    with psycopg2.connect(DB_DSN) as conn:
        with conn.cursor() as cur:
            cur.execute(
                'INSERT INTO telemetry (drone_id, ts, lat, lon, alt, battery) VALUES (%s, %s, %s, %s, %s, %s)',
                (data['drone_id'], datetime.utcnow(), data.get('lat'), data.get('lon'), data.get('alt'), data.get('battery'))
            )
        conn.commit()
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume(queue='telemetry', on_message_callback=callback)
print('Worker started')
channel.start_consuming()
