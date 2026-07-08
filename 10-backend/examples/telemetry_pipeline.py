from fastapi import FastAPI
import pika
import json

app = FastAPI()
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='telemetry')

@app.post('/telemetry')
def receive(data: dict):
    channel.basic_publish(exchange='', routing_key='telemetry', body=json.dumps(data))
    return {'status': 'queued'}
