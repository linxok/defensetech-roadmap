# 13. AI у DefenseTech

> Статус: outline

Застосувати LLM там, де це справді корисно: генерація місій з валідацією схеми, RAG по документації, аналіз логів.

## Що потрібно зрозуміти

- LLM-відповідь — це недовірений ввід: обов’язкова валідація схемою (Pydantic/JSON Schema) і детермінований fallback.
- Prompt має задавати формат, межі й одиниці (метри, градуси) — «зроби місію» без обмежень генерує непридатний JSON.
- RAG: чанкінг документів, ембедінги, пошук top-k, відповідь лише з контексту; для польотної документації — критично.
- Оцінка якості: golden set із 20+ запитів і перевірка схеми; «виглядає добре» — не метрика.
- Безпека: не відправляти в API координати, ключі, персональні дані; для чутливих даних — локальна модель.
- Flight log analysis із LLM: спершу обчислити метрики кодом, потім просити модель пояснити — не навпаки.
- Генерація місій: обмеження висоти, швидкості, кількості точок і геозони перевіряються до завантаження в автопілот.

## Контрольні питання

1. Як валідувати відповідь LLM перед використанням?
2. Що таке golden set і навіщо він для місій?
3. Коли RAG кращий за fine-tuning?
4. Які дані заборонено відправляти в зовнішній API?
5. Чому метрики логу рахуються кодом, а не моделлю?

## Очікуваний результат

Mission Generator із валідацією, офлайн-fallback і тестами (`solution/mission_prompt.py`).

## Зв'язок з capstone

Розділ «Що далі» в `capstone/README.md`: AI-сервіс може генерувати місії для capstone, але з валідацією і журналом рішень.

## Типові помилки

- Довіряти JSON від моделі без валідації — автопілот отримує сміття
- Просити модель порахувати метрики замість коду
- Відправляти в API реальні координати й назви замовників
- Немає fallback: при збої API сервіс повністю непрацездатний

## Первинні джерела

- [OpenAI API reference](https://platform.openai.com/docs/api-reference) — chat completions, JSON mode, timeout
- [Pydantic validators](https://docs.pydantic.dev/latest/concepts/validators/) — валідація відповідей
- [LangChain docs](https://python.langchain.com/docs/get_started/introduction) — RAG-компоненти
- [RAG paper](https://arxiv.org/abs/2005.11401) — retrieval-augmented generation
- [ArduPilot log analysis](https://ardupilot.org/copter/docs/common-downloading-and-analyzing-logs.html) — метрики польоту

## Куди далі

Далі: `lab.md` → `detailed-guide.md` → `checklist.md`.
