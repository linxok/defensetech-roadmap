# Приклади 15: DevOps для флоту

У `examples/` — фрагменти безпечної конфігурації: `Dockerfile`,
`k8s-deployment.yaml`, `prometheus.yml`, `github-actions.yml`, а також
мінімальні `main.py` і `requirements.txt`, щоб образ збирався.
Еталон, який проходить `checks/check_lab.py`: `solution/`.

Збірка образу і перевірка манифесту:

```bash
docker build -t defensetech/telemetry-api:1.0.0 examples/
kubectl apply -f examples/k8s-deployment.yaml --dry-run=client
```
