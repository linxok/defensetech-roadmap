# AI Mission Generator Demo

Генерація польотної місії за текстовим описом через LLM.

## Встановлення

```bash
pip install fastapi uvicorn openai pydantic
```

## Налаштування

```bash
export OPENAI_API_KEY=your_key
```

## Запуск

```bash
uvicorn main:app --reload
```

## Приклад запиту

```bash
curl -X POST http://localhost:8000/generate -H "Content-Type: application/json" -d '{"prompt":"Generate 5 waypoints for a survey at lat 50.45, lon 30.52, altitude 100m"}'
```
