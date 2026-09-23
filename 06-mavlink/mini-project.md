# Мініпроєкт 06: MAVLink: протокол і gateway

## Мета

Production-ready gateway: конфігурація, метрики, тести, Docker.

## Вимоги

1. JSON-схема з версією і валідацією
2. метрики Prometheus: кадри/с, помилки, клієнти
3. Dockerfile і docker-compose з SITL
4. known-answer тести на парсинг кадрів

## Definition of Done

- `docker compose up` піднімає gateway і SITL
- Метрики доступні на `/metrics`
- Битий кадр не валить процес
- README з JSON-прикладом

## Орієнтовний обсяг

16–20 годин

## Публікація

Зробіть окремий публічний репозиторій і додайте його у CV.
