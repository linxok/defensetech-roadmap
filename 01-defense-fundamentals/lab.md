# Лабораторна робота 01: архітектура UAV

## Мета

Побудувати повну схему підсистем дрона з протоколами зв’язку так, щоб
за нею можна було пояснити будь-який потік даних на борту.

## Передумови

- Mermaid-редактор (VS Code extension або mermaid.live).
- SITL встановлено (`sim_vehicle.py` доступний у PATH).

## Кроки

1. Відкрийте `solution/uav-architecture.mmd` як орієнтир структури.
   Діаграма — mermaid (`graph LR` або `graph TD`) зі стрілками `-->`.
2. Намалюйте власну схему: FC, IMU, GPS, ESC/мотори, живлення,
   телеметрія, GCS, companion computer. Підписи вузлів — англійськими
   ідентифікаторами (Flight Controller, GPS, IMU, ESC, Motors,
   Battery/Power, Telemetry Radio, GCS, Companion Computer): саме ці
   ключові слова шукає `checks/check_lab.py`.
3. Підпишіть кожен зв’язок протоколом: MAVLink/UART, PWM/DShot, CSI,
   RTSP, Ethernet.
4. Додайте шар відео: камера → companion → GStreamer → GCS.
5. Перевірте схему (еталон, потім свою теку з `.mmd`):

```bash
python 01-defense-fundamentals/checks/check_lab.py --target 01-defense-fundamentals/solution
python 01-defense-fundamentals/checks/check_lab.py --target <тека з вашим .mmd>
```

6. Запустіть SITL і переконайтеся, що heartbeat доходить до GCS:

```bash
sim_vehicle.py -v ArduCopter --console --map
```

## Очікуваний результат

- Діаграма з 10+ вузлами та підписаними зв’язками.
- SITL-сесія, у якій видно HEARTBEAT і зміну режиму.
- Нотатка з чотирма failsafe-подіями (RC, GCS, battery, geofence).

## Перевірка

`checks/check_lab.py` шукає у схемі всі обов’язкові підсистеми та
мінімум 6 зв’язків. Пропущена підсистема — це не «стиль», а
незавершена лабораторна.

## Розбір збоїв

- `sim_vehicle.py: command not found` — ArduPilot Tools не в PATH;
  див. `docs/setup.md`.
- GCS не бачить heartbeat — перевірте, чи не зайнятий порт 14550
  іншим процесом (`ss -lunp`).
- Діаграма без companion computer типова для веб-розробника: саме
  companion виконує CV і зв’язок, тож без нього схема неповна.
