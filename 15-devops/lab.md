# Лабораторна робота 15: Docker + Kubernetes Deployment

## Мета

Контейнеризувати FastAPI сервіс і розгорнути його в Kubernetes.

## Передумови

- Docker, kubectl, minikube або K3s.

## Кроки

### 1. Dockerfile

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Docker Compose

```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
```

### 3. Kubernetes manifest

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
        - name: api
          image: api:latest
          ports:
            - containerPort: 8000
```

### 4. Збірка і деплой

```bash
docker build -t api:latest .
kubectl apply -f k8s/
```

## Очікуваний результат

- Dockerfile, docker-compose.yml, K8s manifest.
- Сервіс запущено в Kubernetes.
