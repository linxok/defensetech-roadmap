# Приклади 01: Основи DefenseTech і архітектура UAV

У `examples/` — mermaid-схема UAV із companion computer, камерою та
підписаними протоколами. Це коректний зразок, але не готове рішення:
намалюйте власну схему за `lab.md` і перевірте її.

Перегляд: відкрийте `examples/uav-architecture.mmd` у mermaid live editor
або в VS Code (розширення Mermaid) і порівняйте зі своєю.

Перевірка своєї схеми:

```bash
python 01-defense-fundamentals/checks/check_lab.py --target <тека з вашим .mmd>
```

Скрипт шукає всі обов’язкові підсистеми (FC, GPS, IMU, ESC/мотори,
живлення, телеметрія, GCS, companion computer) і мінімум 6 зв’язків.
