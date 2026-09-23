# 04. Python для телеметрії

> Статус: complete

Написати типізований FastAPI-сервіс телеметрії та навчитися коректно поєднувати asyncio з блокуючими бібліотеками (pymavlink, pika).

## Що потрібно зрозуміти

- Pydantic-модель — це контракт: межі `ge/le` відхиляють фізично неможливі дані (наприклад, battery=150) ще до бізнес-логіки.
- `asyncio.to_thread` виносить блокуючий виклик у потік; прямий виклик `recv_match` в async-функції зупиняє весь event loop.
- `asyncio.gather(..., return_exceptions=True)` розсилає дані всім клієнтам, не падаючи через одного; `asyncio.wait` з корутинами — помилка, видалена в Python 3.12.
- TestClient (httpx) дозволяє тестувати API без запуску сервера: перевірка 201/404/422 — це вже контрактні тести.
- Залежності пінуються: `fastapi==0.111.0`, `pymavlink==2.4.41`; оновлення без тестів — джерело нічних регресій.
- Сховище в пам’яті підходить для навчання; для продакшену — PostgreSQL, але інтерфейс доступу має бути один (`TelemetryStore`).

## Контрольні питання

1. Які межі валідності телеметрії і що повертає API на їх порушення?
2. Чому `time.sleep()` не можна викликати в async-обробнику?
3. Як протестувати endpoint без запуску uvicorn?
4. Що зміниться, якщо сховище замінити на PostgreSQL?
5. Чому `except Exception: pass` небезпечний у циклі телеметрії?

## Очікуваний результат

FastAPI-сервіс із валідацією, сховищем і тестами (`solution/main.py`, `checks/check_lab.py`).

## Зв'язок з capstone

Крок 4: backend capstone — той самий патерн (валідація → черга → WebSocket), тому цей модуль є його прототипом.

## Типові помилки

- Створювати `BlockingConnection` при імпорті — сервіс падає без RabbitMQ.
- Повертати 200 замість 201/422: клієнт не розрізняє «прийнято» і «записано».
- Модель без `Field(ge=..., le=...)` пропускає battery=150 і lat=999.
- Один глобальний список без lock при кількох воркерах uvicorn.

## Первинні джерела

- [asyncio — Coroutines and Tasks](https://docs.python.org/3/library/asyncio-task.html) — to_thread, gather, TaskGroup, таймаути
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/) — валідація, залежності, тестування
- [Pydantic docs](https://docs.pydantic.dev/latest/) — Field-обмеження і валідатори
- [pymavlink (source)](https://github.com/ArduPilot/pymavlink) — mavutil, recv_match, діалекти
- [pytest docs](https://docs.pytest.org/en/stable/) — фікстури і параметризація

## Куди далі

Далі: `lab.md` → `detailed-guide.md` → `checklist.md`.
