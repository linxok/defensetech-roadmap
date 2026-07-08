# Mission Planner Demo

Планувальник польотних місій з візуальним редактором waypoints.

## Встановлення

```bash
pip install fastapi uvicorn pydantic
```

## Запуск

```bash
uvicorn main:app --reload
```

## API

- `POST /missions` — створити місію.
- `GET /missions/{id}` — отримати місію.
- `POST /missions/{id}/upload` — конвертувати в MAVLink mission і відправити в SITL.
