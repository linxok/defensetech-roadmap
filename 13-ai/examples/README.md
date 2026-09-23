# Приклади 13: AI у DefenseTech

У `examples/` — офлайн-генерація місії (`mission_prompt.py`) і мінімальний RAG без залежностей (`rag_simple.py`). Еталон із валідацією, LLM і fallback: `solution/mission_prompt.py`.

Запуск: `pip install -r requirements.txt` (venv репозиторію).

## Офлайн-місія

```bash
python mission_prompt.py --lat 50.4501 --lon 30.5234 --alt 100 --count 5
```

Приклад працює без `OPENAI_API_KEY` і без мережі: генерує точки вздовж паралелі та валідує їх Pydantic-моделями.

## RAG на stdlib

```bash
python rag_simple.py
python rag_simple.py --query "geofence area" --top-k 1
```

`rag_simple.py` не використовує langchain: лише токенізація, IDF, TF-IDF і косинусна близькість. Порівняйте його видачу з ембединг-пошуком у `detailed-guide.md`.
