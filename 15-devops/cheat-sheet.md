# Cheat Sheet 15: DevOps для флоту

- `docker build -t app:1.0.0 .`
- `docker compose up --build -d`
- `kubectl apply -f k8s-deployment.yaml`
- `kubectl rollout undo deployment/telemetry-api`
- `docker run --rm trivy image app:1.0.0`
