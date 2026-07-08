# Лабораторна робота 13: LLM Mission Generator

## Мета

Створити сервіс, який за текстовим запитом генерує JSON з waypoints для дрона.

## Передумови

- OpenAI API key або локальна LLM.
- `openai`, `fastapi`, `pydantic`.

## Кроки

### 1. FastAPI сервіс

```python
from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI()
client = OpenAI()

class Prompt(BaseModel):
    text: str

@app.post("/generate-mission")
async def generate_mission(prompt: Prompt):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Generate a drone mission as JSON with waypoints."},
            {"role": "user", "content": prompt.text}
        ]
    )
    return {"mission": response.choices[0].message.content}
```

### 2. Тестування

```bash
curl -X POST http://localhost:8000/generate-mission -H "Content-Type: application/json" -d '{"text":"Generate 4 waypoints around Kyiv at 100m altitude"}'
```

### 3. Постобробка

Розпарсіть JSON відповіді і перевірте валідність координат.

## Очікуваний результат

- FastAPI сервіс.
- Приклад JSON місії.
- README з інструкцією.
