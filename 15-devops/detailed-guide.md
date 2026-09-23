# Розширений гайд 15: DevOps для флоту

Цикл навчання — у `docs/learning-workflow.md`. Нижче — маршрут модуля.

## Порядок проходження

1. Напишіть Dockerfile за чеклістом з `solution/`.
2. Підніміть стек через compose з healthchecks.
3. Опишіть k8s Deployment із probes і resources.
4. Додайте CI-job збірки образу.
5. Проженіть `checks/check_lab.py`.

## Орієнтовний час

1–2 тижні (8–12 годин)

## Артефакти модуля

- `Dockerfile`
- `docker-compose.yml`
- `k8s-deployment.yaml`
- CI-workflow

## Пастки цього модуля

- `COPY . .` до `pip install` ламає кеш
- compose без `condition: service_healthy` — гонки
