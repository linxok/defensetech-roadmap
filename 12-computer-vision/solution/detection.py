"""Детекція об'єктів YOLOv8 (ONNX) через OpenCV DNN.

Підготовка моделі:

    pip install ultralytics
    yolo export model=yolov8n.pt format=onnx imgsz=640

Запуск:

    python yolo_opencv.py --model yolov8n.onnx --source 0
    python yolo_opencv.py --model yolov8n.onnx --source frame.jpg --output out.jpg

Примітка: OpenCV DNN не потребує GPU; на Jetson використовуйте
TensorRT-провайдера окремо (див. resources.md).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cv2
import numpy as np

COCO_NAMES = (
    'person,bicycle,car,motorcycle,airplane,bus,train,truck,boat,traffic light,'
    'fire hydrant,stop sign,parking meter,bench,bird,cat,dog,horse,sheep,cow,'
    'elephant,bear,zebra,giraffe,backpack,umbrella,handbag,tie,suitcase,frisbee,'
    'skis,snowboard,sports ball,kite,baseball bat,baseball glove,skateboard,'
    'surfboard,tennis racket,bottle,wine glass,cup,fork,knife,spoon,bowl,banana,'
    'apple,sandwich,orange,broccoli,carrot,hot dog,pizza,donut,cake,chair,couch,'
    'potted plant,bed,dining table,toilet,tv,laptop,mouse,remote,keyboard,'
    'cell phone,microwave,oven,toaster,sink,refrigerator,book,clock,vase,'
    'scissors,teddy bear,hair drier,toothbrush'
).split(',')

INPUT_SIZE = 640


def letterbox(frame: np.ndarray, size: int = INPUT_SIZE) -> tuple[np.ndarray, float, int, int]:
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
    """Повертає [(class_id, confidence, (x1, y1, x2, y2))] у координатах input_size."""
    predictions = np.squeeze(output).T  # (8400, 84): xywh + 80 scores
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


def draw(frame: np.ndarray, detections: list[tuple[int, float, tuple[int, int, int, int]]]) -> np.ndarray:
    for class_id, confidence, (x1, y1, x2, y2) in detections:
        label = f'{COCO_NAMES[class_id]} {confidence:.2f}'
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, label, (x1, max(20, y1 - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    return frame


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', type=Path, required=True)
    parser.add_argument('--source', default='0', help='індекс камери або шлях до файлу')
    parser.add_argument('--output', type=Path, help='куди зберегти кадр/відео')
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

    printed = False
    try:
        while True:
            ok, frame = capture.read()
            if not ok:
                break
            blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (INPUT_SIZE, INPUT_SIZE),
                                         swapRB=True, crop=False)
            net.setInput(blob)
            output = net.forward()
            detections = scale_to_frame(
                postprocess(output, args.conf), *letterbox(frame)[1:], frame.shape
            )
            if not printed:
                print(f'frame {frame.shape[1]}x{frame.shape[0]}: '
                      f'{len(detections)} detections')
                printed = True
            if args.output and source != 0 or args.output:
                cv2.imwrite(str(args.output), draw(frame, detections))
                print(f'saved: {args.output}')
                break
            cv2.imshow('detection', draw(frame, detections))
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        capture.release()
        cv2.destroyAllWindows()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
