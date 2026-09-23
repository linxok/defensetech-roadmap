# Cheat Sheet 13: AI у DefenseTech

- `client.chat.completions.create(model=..., response_format={"type": "json_object"})`
- `Mission.model_validate(raw)` — валідація відповіді
- `timeout=30` на кожен зовнішній виклик
- `json.dumps(mission.model_dump(), indent=2)`
- `os.environ["OPENAI_API_KEY"]` — ключ лише з env
