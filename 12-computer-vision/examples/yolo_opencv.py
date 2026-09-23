"""Спрощена демонстрація YOLOv8 (ONNX) через OpenCV DNN.

Показує мінімальний конвеєр для одного кадру: letterbox 640×640,
декодування виходу (1, 84, N), поріг впевненості та жадібний NMS.
Повний конвеєр із масштабуванням координат до кадру — у `solution/detection.py`.

Підготовка моделі:

    pip install ultralytics
    yolo export model=yolov8n.pt format=onnx imgsz=640

Запуск:

    python yolo_opencv.py --model yolov8n.onnx --source frame.jpg
    python yolo_opencv.py --model yolov8n.onnx --source frame.jpg --output out.jpg
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cv2
import numpy as np

INPUT_SIZE = 640


def letterbox(frame: np.ndarray, size: int = INPUT_SIZE) -> tuple[np.ndarray, float, int, int]:
    """Масштабує кадр у квадрат size×size без спотворення пропорцій."""
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
    """Вибирає найкращий клас для кожної рамки і придушує перекриття жадібним NMS."""
    predictions = np.squeeze(output).T  # (N, 84): xywh + 80 scores
    scores = predictions[:, 4:]
    class_ids = scores.argmax(axis=1)
    confidences = scores[np.arange(len(scores)), class_ids]
    keep = confidences >= conf_threshold
    boxes = predictions[keep, :4]
    confidences = confidences[keep]
    class_ids = class_ids[keep]

    xyxy = np.empty_like(boxes)
    xyxy[:, 0] = boxes[:, 0] - boxes[:, 2] / 2
    xyxy[:, 1] = boxes[:, 1] - boxes[:, 3] / 2
    xyxy[:, 2] = boxes[:, 0] + boxes[:, 2] / 2
    xyxy[:, 3] = boxes[:, 1] + boxes[:, 3] / 2

    order = confidences.argsort()[::-1]
    result = []
    while order.size:
        best = order[0]
        result.append((int(class_ids[best]), float(confidences[best]),
                       tuple(int(v) for v in xyxy[best])))
        rest = order[1:]
        if rest.size == 0:
            break
        x1 = np.maximum(xyxy[best, 0], xyxy[rest, 0])
        y1 = np.maximum(xyxy[best, 1], xyxy[rest, 1])
        x2 = np.minimum(xyxy[best, 2], xyxy[rest, 2])
        y2 = np.minimum(xyxy[best, 3], xyxy[rest, 3])
        intersection = np.clip(x2 - x1, 0, None) * np.clip(y2 - y1, 0, None)
        area_best = (xyxy[best, 2] - xyxy[best, 0]) * (xyxy[best, 3] - xyxy[best, 1])
        area_rest = (xyxy[rest, 2] - xyxy[rest, 0]) * (xyxy[rest, 3] - xyxy[rest, 1])
        iou = intersection / (area_best + area_rest - intersection)
        order = rest[iou <= iou_threshold]
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', type=Path, required=True)
    parser.add_argument('--source', default='0', help='зображення або індекс камери')
    parser.add_argument('--output', type=Path, help='куди зберегти розмічений кадр')
    parser.add_argument('--conf', type=float, default=0.4)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.model.is_file():
        print(f'model not found: {args.model}', file=sys.stderr)
        return 1
    net = cv2.dnn.readNetFromONNX(str(args.model))

    source: int | str = int(args.source) if args.source.isdigit() else args.source
    capture = cv2.VideoCapture(source)
    if not capture.isOpened():
        print(f'cannot open source: {args.source}', file=sys.stderr)
        return 1
    try:
        ok, frame = capture.read()
    finally:
        capture.release()
    if not ok:
        print('cannot read frame', file=sys.stderr)
        return 1

    canvas, _, _, _ = letterbox(frame)
    blob = cv2.dnn.blobFromImage(canvas, 1 / 255.0, (INPUT_SIZE, INPUT_SIZE),
                                 swapRB=True, crop=False)
    net.setInput(blob)
    detections = postprocess(net.forward(), args.conf)
    print(f'{len(detections)} detections (координати 640×640, без масштабування до кадру)')

    for class_id, confidence, (x1, y1, x2, y2) in detections:
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, f'{class_id} {confidence:.2f}', (x1, max(20, y1 - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    if args.output:
        cv2.imwrite(str(args.output), frame)
        print(f'saved: {args.output}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
