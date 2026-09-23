# Quickstart

Швидкий старт курсу **DefenseTech Roadmap**. Рекомендований трек —
Drone / Autopilot Software.

## 1. Клонування

```bash
git clone https://github.com/linxok/defensetech-roadmap.git
cd defensetech-roadmap
```

## 2. Середовище

Деталі — у `docs/setup.md`. Коротко:

```bash
sudo apt update
sudo apt install -y git build-essential cmake python3-pip python3-venv docker.io
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
```

Перевірка, що все на місці:

```bash
python scripts/verify_structure.py
python scripts/run_lab_checks.py
```

## 3. Перший модуль

```bash
cat 00-introduction/README.md
cat 00-introduction/lab.md
python 00-introduction/checks/check_lab.py --target 00-introduction/solution
```

Заповніть `plan.md` за еталоном `00-introduction/solution/plan-example.md`.

## 4. Порядок проходження

1. Профільні модулі 04–09 — глибоко, з `checks/` і мініпроєктами.
2. Решта — оглядово, на рівні README і checklist.
3. Після кожного модуля перевіряйте `checklist.md` і оновлюйте capstone.

## 5. Capstone

```bash
cd capstone
docker compose up --build
```

Відкрийте http://localhost:3000 (UI), http://localhost:8000/docs (API),
http://localhost:15672 (RabbitMQ). Режим справжнього SITL:
`COMPOSE_PROFILES=sitl docker compose up --build`.

## 6. Сайт курсу

```bash
pip install -r requirements-docs.txt
python scripts/prepare_docs.py
mkdocs serve -f .mkdocs-build/mkdocs.yml
```

## 7. Публікація

Ведіть власний репозиторій-трекер: план, нотатки, лабораторні.
Один публічний артефакт на тиждень — мінімум. Портфоліо — у `16-projects/`.
