# Приклади 16: Портфоліо-проєкти

Коду в `examples/` немає: стартовий шаблон репозиторію — у
`solution/starter-template/`, і саме його перевіряє `checks/check_lab.py`.

Прогін шаблону:

```bash
cd 16-projects/solution/starter-template
pip install -r requirements.txt -r requirements-dev.txt
pytest -q
```

Перевірка лабораторної:

```bash
python 16-projects/checks/check_lab.py --target 16-projects/solution
```
