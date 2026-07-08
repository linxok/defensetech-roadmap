# Лабораторна робота 12: Realtime YOLO Detection

## Мета

Запустити YOLO для детекції об'єктів у відеопотоці з веб-камери.

## Передумови

- Python 3.11+
- `ultralytics`, `opencv-python`

## Кроки

### 1. Встановлення

```bash
pip install ultralytics opencv-python
```

### 2. Скрипт детекції

```python
import cv2
from ultralytics import YOLO

model = YOLO('yolov8n.pt')
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    results = model(frame)
    annotated = results[0].plot()
    cv2.imshow('YOLO', annotated)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

### 3. Збереження результатів

```python
cv2.imwrite('detection.jpg', annotated)
```

### 4. Тестування

1. Запустіть скрипт.
2. Покажіть камері об'єкти.
3. Переконайтеся, що bounding boxes з’являються.

## Очікуваний результат

- Робочий YOLO скрипт.
- Збережений скріншот детекції.
- README.
