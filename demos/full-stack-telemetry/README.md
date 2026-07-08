# Full-Stack Telemetry Demo

Повний стек: MAVLink Gateway → FastAPI backend → PostgreSQL → RabbitMQ → Worker → React frontend.

## Запуск

```bash
docker-compose up --build
```

## Компоненти

- `gateway/` — UDP → HTTP bridge.
- `backend/` — FastAPI REST + WebSocket.
- `worker/` — RabbitMQ consumer → PostgreSQL.
- `frontend/` — React + Leaflet + WebSocket.
- `k8s/` — Kubernetes маніфести.
