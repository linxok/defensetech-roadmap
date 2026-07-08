import json
import pika
from fastapi import FastAPI, WebSocket

app = FastAPI()
app.state.ws_clients = []

connection = pika.BlockingConnection(pika.URLParameters('amqp://guest:guest@rabbitmq:5672/'))
channel = connection.channel()
channel.queue_declare(queue='telemetry')

@app.post('/telemetry')
async def receive_telemetry(data: dict):
    channel.basic_publish(exchange='', routing_key='telemetry', body=json.dumps(data))
    for c in app.state.ws_clients:
        await c.send_text(json.dumps(data))
    return {'status': 'queued'}

@app.websocket('/ws')
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    app.state.ws_clients.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    finally:
        app.state.ws_clients.remove(websocket)
