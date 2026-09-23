# Проєкт 09-drone-ai-agent: Drone AI Agent

## Опис

Агент на основі LLM/VLM для планування місій та аналізу ситуації.

## Функціональність

- LLM integration
- RAG over manuals
- Vision analysis
- Mission generation
- Human-in-the-loop
- Safety checks

## Архітектура

```mermaid
graph LR
    A[Drone] --> B[Gateway]
    B --> C[Queue]
    C --> D[Workers]
    D --> E[Database]
    E --> F[API]
    F --> G[Dashboard]
```

## Технологічний стек

- Python / FastAPI або Node.js / NestJS
- PostgreSQL / Redis
- RabbitMQ / Kafka
- Docker / Kubernetes
- React / Next.js / Leaflet
- Prometheus / Grafana

## Етапи реалізації

1. Проєктування API та схеми даних.
2. Реалізація core функціоналу.
3. Інтеграція з дроном / SITL.
4. Тестування та дебаг.
5. Документація, Docker, CI/CD.
6. Деплой та демо.

## Критерії готовності

- [ ] Код у публічному репозиторії.
- [ ] README з інструкцією запуску.
- [ ] Docker Compose або Kubernetes маніфести.
- [ ] CI/CD pipeline.
- [ ] Тести або чекліст якості.
- [ ] Демо: скріншот, відео або live URL.

## Критерії приймання (DoD)

- [ ] Відповідь LLM валідується схемою; невалідна — відхиляється
- [ ] Геозона перевіряється кодом до завантаження місії
- [ ] Сервіс працює без зовнішнього API (офлайн-fallback)
- [ ] У логах немає координат замовника і секретів
- [ ] Golden set із 10 запитів проходить регресійно

## Стартовий код

- `13-ai/solution/mission_prompt.py` — валідація і fallback
- `02-mission-service` — приклад схеми місії

## Рекомендації

- Починайте з мінімального viable продукту.
- Використовуйте SITL для тестування без реального дрона.
- Додайте логування та моніторинг з першого дня.
- Документуйте API з OpenAPI/Swagger.
- Покрийте код тестами поступово.

## Складність

**Рівень:** Intermediate — Advanced
**Час:** 2–6 тижнів залежно від глибини.
