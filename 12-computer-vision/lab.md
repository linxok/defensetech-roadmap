# Лабораторна робота 12: Realtime YOLO Detection

## Мета

Реалізувати чисту постобробку YOLOv8 (ONNX) у `detection.py`, запустити детекцію на відео й виміряти FPS.

## Передумови

- Python 3.11+.
- `opencv-python==4.10.0.84`, `numpy==1.26.4` (кореневий `requirements.txt`); `ultralytics==8.2.48` — лише для експорту моделі в ONNX.

```bash
pip install opencv-python==4.10.0.84 numpy==1.26.4
pip install ultralytics==8.2.48
```

## Кроки

### 1. Робоча тека

```bash
mkdir -p ~/drone-labs/12-yolo
cd ~/drone-labs/12-yolo
```

### 2. Модуль `detection.py`

Створіть файл `detection.py` з функціями `letterbox`, `postprocess` і `scale_to_frame`. Саме ці імена та сигнатури перевіряє `checks/check_lab.py`.

```python
"""Постобробка YOLOv8 (ONNX) через OpenCV DNN."""

from __future__ import annotations

import cv2
import numpy as np

INPUT_SIZE = 640


def letterbox(frame: np.ndarray, size: int = INPUT_SIZE) -> tuple[np.ndarray, float, int, int]:
    """Масштабує кадр без спотворення пропорцій у квадрат size×size.

    Повертає (canvas, ratio, pad_w, pad_h): canvas — тензор (size, size, 3)
    із сірими полями 114, ratio — коефіцієнт масштабу, pad_w/pad_h — поля зліва/зверху.
    """
    height, width = frame.shape[:2]
    ratio = min(size / height, size / width)
    new_w, new_h = int(round(width * ratio)), int(round(height * ratio))
    resized = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
    pad_w, pad_h = (size - new_w) // 2, (size - new_h) // 2
    canvas = np.full((size, size, 3), 114, dtype=np.uint8)
    canvas[pad_h:pad_h + new_h, pad_w:pad_w + new_w] = resized
    return canvas, ratio, pad_w, pad_h


def postprocess(
    output: np.ndarray, conf_threshold: float = 0.4, iou_threshold: float = 0.5
) -> list[tuple[int, float, tuple[int, int, int, int]]]:
    """Декодує вихід (1, 84, N) у [(class_id, confidence, (x1, y1, x2, y2))].

    Перші 4 значення кожного стовпця — xywh, решта 80 — scores класів.
    Координати залишаються в системі входу 640×640; NMS отримує xywh.
    """
    predictions = np.squeeze(output).T  # (N, 84): xywh + 80 scores
    boxes = predictions[:, :4]
    scores = predictions[:, 4:]
    class_ids = scores.argmax(axis=1)
    confidences = scores[np.arange(len(scores)), class_ids]

    keep = confidences >= conf_threshold
    if not keep.any():
        return []

    boxes_xywh = boxes[keep]
    confidences = confidences[keep]
    class_ids = class_ids[keep]
    xyxy = np.empty_like(boxes_xywh)
    xyxy[:, 0] = boxes_xywh[:, 0] - boxes_xywh[:, 2] / 2
    xyxy[:, 1] = boxes_xywh[:, 1] - boxes_xywh[:, 3] / 2
    xyxy[:, 2] = boxes_xywh[:, 0] + boxes_xywh[:, 2] / 2
    xyxy[:, 3] = boxes_xywh[:, 1] + boxes_xywh[:, 3] / 2

    indices = cv2.dnn.NMSBoxes(
        boxes_xywh.tolist(), confidences.tolist(), conf_threshold, iou_threshold
    )
    result: list[tuple[int, float, tuple[int, int, int, int]]] = []
    for index in np.array(indices).flatten():
        x1, y1, x2, y2 = (int(v) for v in xyxy[index])
        result.append((int(class_ids[index]), float(confidences[index]), (x1, y1, x2, y2)))
    return result


def scale_to_frame(
    detections: list[tuple[int, float, tuple[int, int, int, int]]],
    ratio: float,
    pad_w: int,
    pad_h: int,
    frame_shape: tuple[int, ...],
) -> list[tuple[int, float, tuple[int, int, int, int]]]:
    """Повертає детекції в координатах кадру, обрізані до його меж."""
    height, width = frame_shape[:2]
    scaled = []
    for class_id, confidence, (x1, y1, x2, y2) in detections:
        box = (
            max(0, min(width, int((x1 - pad_w) / ratio))),
            max(0, min(height, int((y1 - pad_h) / ratio))),
            max(0, min(width, int((x2 - pad_w) / ratio))),
            max(0, min(height, int((y2 - pad_h) / ratio))),
        )
        scaled.append((class_id, confidence, box))
    return scaled
```

### 3. Перевірка функцій

Скопіюйте `detection.py` у робочу теку (вона вже створена) і проженіть контрактну перевірку:

```bash
python checks/check_lab.py --target ~/drone-labs/12-yolo
```

Очікуваний вивід: `PASS: letterbox, NMS і масштабування працюють коректно`. Перевірка синтетична: без моделі, камери й мережі; вона вимагає, щоб `letterbox` на кадрі 720×1280 повертав canvas `(640, 640, 3)`, `ratio=0.5`, `pad=(0, 140)`.

### 4. Експорт моделі в ONNX

```bash
yolo export model=yolov8n.pt format=onnx imgsz=640
```

У робочій теці з'явиться `yolov8n.onnx` (вихід моделі — `(1, 84, 8400)`).

### 5. Детекція на кадрі

Конвеєр: `letterbox` → `blobFromImage` → `net.forward()` → `postprocess` → `scale_to_frame`.

```python
import cv2
from detection import letterbox, postprocess, scale_to_frame

net = cv2.dnn.readNetFromONNX('yolov8n.onnx')
frame = cv2.imread('frame.jpg')
canvas, ratio, pad_w, pad_h = letterbox(frame, 640)
blob = cv2.dnn.blobFromImage(canvas, 1 / 255.0, (640, 640), swapRB=True, crop=False)
net.setInput(blob)
output = net.forward()
detections = scale_to_frame(
    postprocess(output, conf_threshold=0.4), ratio, pad_w, pad_h, frame.shape
)
for class_id, confidence, box in detections:
    print(f'class={class_id} conf={confidence:.2f} box={box}')
cv2.imwrite('detection.jpg', frame)
```

### 6. Вимірювання FPS

Без прогріву перший інференс у 3–5 разів повільніший, тому спершу кілька прогрівних прогонів, потім замір на 30 кадрах через `time.perf_counter`.

```python
import time

import cv2
import numpy as np

from detection import letterbox, postprocess

WARMUP = 5
FRAMES = 30

net = cv2.dnn.readNetFromONNX('yolov8n.onnx')
frame = np.zeros((720, 1280, 3), dtype=np.uint8)
canvas, _, _, _ = letterbox(frame, 640)


def infer():
    blob = cv2.dnn.blobFromImage(canvas, 1 / 255.0, (640, 640), swapRB=True, crop=False)
    net.setInput(blob)
    postprocess(net.forward(), conf_threshold=0.4)


for _ in range(WARMUP):
    infer()

start = time.perf_counter()
for _ in range(FRAMES):
    infer()
elapsed = time.perf_counter() - start

print(f'{FRAMES} frames: {elapsed:.2f}s -> {FRAMES / elapsed:.1f} FPS')
print(f'latency: {elapsed / FRAMES * 1000:.1f} ms/frame')
```

Запишіть отримані FPS і latency у README своєї лабораторної — це і є «виміряний FPS» модуля.

## Перевірка

```bash
python checks/check_lab.py --target ~/drone-labs/12-yolo
python checks/check_lab.py --target solution
```

## Розбір збоїв

- `cv2.error: ... Can't parse 'bboxes'. Sequence item with index 0 has a wrong type` — у `cv2.dnn.NMSBoxes` передали numpy-масив; потрібен список: `boxes_xywh.tolist()`.
- Рамки зміщені або стиснуті — координати масштабовані назад без урахування `pad_w`/`pad_h` з `letterbox`.
- Рамки дублюються — NMS отримав xyxy замість xywh або `iou_threshold` зависокий.
- Нуль детекцій на реальному кадрі — клас вибрано не через `scores.argmax`, а через перший score-стовпець, або `conf_threshold` зависокий.

## Очікуваний результат

- `detection.py` із трьома функціями, що проходить `checks/check_lab.py`.
- `yolov8n.onnx` і збережений кадр із рамками (`detection.jpg`).
- Записане число FPS після прогріву.
