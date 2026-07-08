# Flight Log Analyzer Demo

Аналіз польотних журналів PX4 (.ulg) та ArduPilot (.bin).

## Встановлення

```bash
pip install pyulog pandas matplotlib
```

## Запуск

```bash
python analyze.py --log path/to/log.ulg --output report.html
```

## Можливості

- Вивід топіків.
- Графіки висоти, швидкості, батареї.
- Виявлення аномалій (наприклад, різке падіння батареї).
