# Kubernetes manifests

Образи збілдовані локально (`docker compose -f ../docker-compose.yml build`)
мають теги `capstone-backend:1.0.0`, `capstone-gateway:1.0.0`,
`capstone-frontend:1.0.0`. Для локального кластера завантажте їх:

```bash
kind load docker-image capstone-backend:1.0.0 capstone-gateway:1.0.0 capstone-frontend:1.0.0
```

Секрет для БД (приклад dev-оточення):

```bash
kubectl -n drone-telemetry create secret generic db-secret \
  --from-literal=url='postgresql://drone:secret@postgres:5432/drone'
```

Застосування маніфестів:

```bash
kubectl apply -f namespace.yaml
kubectl apply -f postgres.yaml -f rabbitmq.yaml
kubectl apply -f backend.yaml -f worker.yaml -f gateway.yaml -f frontend.yaml
```

Перевірка:

```bash
kubectl -n drone-telemetry get pods
kubectl -n drone-telemetry port-forward svc/backend 8000:8000
kubectl -n drone-telemetry port-forward svc/frontend 3000:3000
```

Браузер відкриває http://localhost:3000; WebSocket іде на
`ws://localhost:8000/ws`, тому port-forward backend має бути активним.

Sim/SITL у Kubernetes не входить: MAVLink-джерело (sim або SITL)
запускається поза кластером і надсилає UDP на Service gateway.
