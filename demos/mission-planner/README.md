# Mission Planner Demo

Мінімальний REST API для зберігання польотних місій (in-memory).
Демо працює повністю офлайн: зовнішніх з'єднань немає, SITL не потрібен.

## Встановлення

```bash
pip install -r requirements.txt
```

## Запуск

```bash
uvicorn main:app --reload
```

## API

- `POST /missions` — створити місію (назва і щонайменше 2 waypoints); повертає `id`.
- `GET /missions/{id}` — отримати місію.
- `POST /missions/{id}/upload` — підтвердити прийом місії (повертає `status` і кількість waypoints).

Приклад:

```bash
curl -X POST http://127.0.0.1:8000/missions -H "Content-Type: application/json" \
  -d '{"name":"patrol","waypoints":[{"lat":50.45,"lon":30.52,"alt":100},{"lat":50.46,"lon":30.53,"alt":120}]}'
```

## Обмеження

- Місії живуть лише в пам'яті процесу й зникають після перезапуску.
- Конверсії в MAVLink і відправки в SITL немає: `upload` лише валідує місію та підтверджує прийом. Повні версії — `16-projects/02-mission-service-mission-service.md` і `10-backend/lab.md`.
