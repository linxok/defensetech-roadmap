#!/usr/bin/env python3
"""Перевірка лабораторної 12: постобробка YOLO-детекцій.

Контракт (див. lab.md): у `detection.py` є чисті функції
`letterbox`, `postprocess`, `scale_to_frame`, які можна перевірити
без моделі та камери на синтетичному тензорі.

Запуск:
    python checks/check_lab.py --target solution
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
MODULE = HERE.parent


def fail(message: str) -> None:
    print(f'FAIL: {message}')
    raise SystemExit(1)


def load_module(target: Path):
    path = target / 'detection.py'
    if not path.is_file():
        fail(f'{path} не існує')
    spec = importlib.util.spec_from_file_location('student_detection', path)
    module = importlib.util.module_from_spec(spec)
    sys.modules['student_detection'] = module
    try:
        spec.loader.exec_module(module)
    except Exception as exc:  # noqa: BLE001
        fail(f'модуль не імпортується: {exc!r}')
    for attr in ('letterbox', 'postprocess', 'scale_to_frame'):
        if not hasattr(module, attr):
            fail(f'у модулі немає `{attr}`')
    return module


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', type=Path, default=MODULE / 'solution')
    args = parser.parse_args()

    module = load_module(args.target)

    frame = np.zeros((720, 1280, 3), dtype=np.uint8)
    canvas, ratio, pad_w, pad_h = module.letterbox(frame, 640)
    if canvas.shape != (640, 640, 3):
        fail(f'letterbox має повертати 640x640, отримано {canvas.shape}')
    if abs(ratio - 0.5) > 1e-6 or pad_w != 0 or pad_h != 140:
        fail(f'невірний letterbox: ratio={ratio}, pad=({pad_w}, {pad_h})')

    predictions = np.zeros((1, 84, 10), dtype=np.float32)
    predictions[0, :4, 0] = (320.0, 320.0, 100.0, 200.0)  # cx, cy, w, h
    predictions[0, 4, 0] = 0.9  # class 0 (person)
    predictions[0, 4, 1] = 0.02
    predictions[0, :4, 1] = (330.0, 330.0, 90.0, 180.0)
    predictions[0, 6, 1] = 0.8  # class 2 (car), майже та сама рамка
    predictions[0, 6, 0] = 0.01

    detections = module.postprocess(predictions, conf_threshold=0.4, iou_threshold=0.5)
    if len(detections) != 1:
        fail(f'NMS має придушити дубль, отримано {len(detections)} детекцій')
    class_id, confidence, box = detections[0]
    if class_id != 0 or abs(confidence - 0.9) > 1e-5:
        fail(f'невірна детекція після NMS: {detections[0]}')
    if box != (270, 220, 370, 420):
        fail(f'невірні координати xyxy: {box}')

    scaled = module.scale_to_frame(detections, 0.5, 0, 140, frame.shape)
    if scaled[0][2] != (540, 160, 740, 560):
        fail(f'невірне масштабування до кадру: {scaled[0][2]}')

    empty = module.postprocess(np.zeros((1, 84, 4), dtype=np.float32))
    if empty:
        fail('на нульовому тензорі не має бути детекцій (або пропустіть цей модуль)')

    print('PASS: letterbox, NMS і масштабування працюють коректно')
    return 0


if __name__ == '__main__':
    sys.exit(main())
