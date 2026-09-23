# Лабораторна робота 15: Docker + Kubernetes Deployment

## Мета

Контейнеризувати FastAPI сервіс і розгорнути його в Kubernetes.

## Передумови

- Docker, kubectl, minikube або K3s.
- Python 3.12 і FastAPI-застосунок із `main.py`, у якого є `/health`.

## Структура

`checks/check_lab.py` шукає рівно три файли в теці лабораторної
(у репозиторії — `solution/`):

- `Dockerfile`;
- `docker-compose.yml`;
- `k8s-deployment.yaml`.

Додатково сервіс має `main.py` з FastAPI і піновані `requirements.txt`, щоб контейнер збирався.

## Кроки

### 1. Сервіс

`requirements.txt`:

```text
fastapi==0.111.0
uvicorn[standard]==0.30.0
```

`main.py` — ендпоінт `/health`, який використають HEALTHCHECK, compose і probes:

```python
"""Мінімальний FastAPI-сервіс для лабораторної 15.

Ендпоінт `/health` використовують HEALTHCHECK у Dockerfile,
healthcheck у compose і probes у k8s-манифесті.

Запуск локально:

    uvicorn main:app --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

from fastapi import FastAPI

app = FastAPI(title='Telemetry API')


@app.get('/health')
async def health() -> dict[str, str]:
    return {'status': 'ok'}
```

### 2. Dockerfile

Базовий образ пінований (не `:latest`), контейнер працює від non-root `USER`, є `HEALTHCHECK` на `/health`:

```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd --create-home --uid 10001 app
USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 3. docker-compose.yml

Compose піднімає API, PostgreSQL і Redis; у stateful-сервісів є healthcheck, API чекає на готовність БД, жодного `:latest`:

```yaml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://app:secret@db:5432/app
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)"]
      interval: 10s
      retries: 6
  db:
    image: postgres:16
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: app
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app -d app"]
      interval: 5s
      retries: 12
  cache:
    image: redis:7
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      retries: 12
```

### 4. k8s-deployment.yaml

Deployment має пінований образ, `resources.requests` і `limits`, readiness/liveness probes на `/health` та `securityContext.runAsNonRoot`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: telemetry-api
  labels:
    app: telemetry-api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: telemetry-api
  template:
    metadata:
      labels:
        app: telemetry-api
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 10001
      containers:
        - name: api
          image: defensetech/telemetry-api:1.0.0
          ports:
            - containerPort: 8000
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: db-secret
                  key: url
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 500m
              memory: 256Mi
          readinessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 15
            periodSeconds: 20
---
apiVersion: v1
kind: Service
metadata:
  name: telemetry-api
spec:
  selector:
    app: telemetry-api
  ports:
    - port: 80
      targetPort: 8000
  type: ClusterIP
```

### 5. Збірка і деплой

Тег образу скрізь однаковий — `defensetech/telemetry-api:1.0.0`, без `:latest`:

```bash
docker build -t defensetech/telemetry-api:1.0.0 .
docker compose -f docker-compose.yml up --build -d
minikube image load defensetech/telemetry-api:1.0.0
kubectl apply -f k8s-deployment.yaml
```

## Перевірка

Перевірте артефакти і зберіть образ:

```bash
python checks/check_lab.py --target solution
docker compose -f solution/docker-compose.yml build
```

У `--target` вкажіть свою теку з трьома файлами (у репозиторії — `solution`). Очікування: non-root образ, healthchecks, probes і resources у манифесті, жодного `:latest`.

## Розбір збоїв

- Образ падає на healthcheck — немає `/health`
- Compose стартує до готовності БД — потрібен `condition: service_healthy`
- `:latest` у манифесті — невідтворюваний деплой
- `kubectl apply -f k8s/` — такої теки немає; манифест лежить у файлі `k8s-deployment.yaml`

## Очікуваний результат

- `Dockerfile`, `docker-compose.yml`, `k8s-deployment.yaml`.
- Образ `defensetech/telemetry-api:1.0.0` збирається і працює non-root.
- Сервіс запущено в Kubernetes.
