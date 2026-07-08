# Quickstart

Швидкий старт для курсу **DefenseTech Roadmap**.

## 1. Клонування та огляд

```bash
git clone https://github.com/your-username/defensetech-roadmap.git
cd defensetech-roadmap
ls
```

## 2. Налаштування середовища

Детальна інструкція в `docs/setup.md`. Коротко:

```bash
sudo apt update
sudo apt install -y git build-essential cmake python3-pip python3-venv docker.io docker-compose
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 3. Перший модуль

Почніть з `00-introduction/`:

```bash
cat 00-introduction/README.md
cat 00-introduction/lab.md
cat 00-introduction/checklist.md
```

## 4. Наступні модулі

Проходьте модулі по порядку. Виконуйте лабораторні, практику, домашні завдання і мініпроєкти.

## 5. Портфоліо

Коли пройдете 5–7 модулів, розпочніть портфоліо-проєкти з `16-projects/`.

## 6. Публікація

Ведіть власний репозиторій з нотатками і проєктами. Закріпіть найкращі роботи на GitHub.

## 7. Сайт курсу

```bash
pip install mkdocs-material
mkdocs serve
```

Відкрийте http://localhost:8000.
