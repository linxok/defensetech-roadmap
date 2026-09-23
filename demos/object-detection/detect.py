"""Детекція YOLO через Ultralytics (демо).

Запуск:

    python detect.py --source video.mp4 --output out.mp4
    python detect.py --source 0                    # вебкамера

Порівняйте з `12-computer-vision/examples/yolo_opencv.py`, де той самий
YOLO виконується через OpenCV DNN без залежності від ultralytics.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cv2


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', default='0', help='індекс камери або шлях до файлу')
    parser.add_argument('--model', default='yolov8n.pt')
    parser.add_argument('--output', type=Path, help='файл для запису результату')
    parser.add_argument('--conf', type=float, default=0.4)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        from ultralytics import YOLO
    except ImportError:
        print('ultralytics не встановлено: pip install -r requirements.txt', file=sys.stderr)
        return 1

    if not Path(args.model).is_file() and args.model.endswith('.pt'):
        print(f'model not found: {args.model}', file=sys.stderr)
        return 1

    model = YOLO(args.model)
    source: int | str = int(args.source) if args.source.isdigit() else args.source
    capture = cv2.VideoCapture(source)
    if not capture.isOpened():
        print(f'cannot open source: {args.source}', file=sys.stderr)
        return 1

    writer = None
    if args.output:
        width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = capture.get(cv2.CAP_PROP_FPS) or 30
        writer = cv2.VideoWriter(
            str(args.output), cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height)
        )

    frames = 0
    try:
        while True:
            ok, frame = capture.read()
            if not ok:
                break
            results = model(frame, conf=args.conf, verbose=False)
            annotated = results[0].plot()
            frames += 1
            if writer is not None:
                writer.write(annotated)
                if frames % 30 == 0:
                    print(f'processed {frames} frames')
                continue
            cv2.imshow('Detection', annotated)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        capture.release()
        if writer is not None:
            writer.release()
        cv2.destroyAllWindows()

    print(f'done: {frames} frames')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
