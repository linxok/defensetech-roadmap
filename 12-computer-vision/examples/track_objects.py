"""Трекінг об'єкта у відео через OpenCV TrackerMIL.

У opencv-python 4.10 `cv2.TrackerCSRT_create()` відсутній в основному
namespace, тому для переносимого прикладу використовується `cv2.TrackerMIL_create()`.

Запуск:

    python track_objects.py --video path/to/video.mp4
    python track_objects.py --video 0

У вікні з першим кадром виділіть рамку мишею (Enter/Space — підтвердити).
Вихід — клавіша q або кінець відео.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cv2


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--video', required=True, help='шлях до файлу або індекс камери')
    parser.add_argument('--output', type=Path, help='записати розмічене відео')
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source: int | str = int(args.video) if args.video.isdigit() else args.video
    capture = cv2.VideoCapture(source)
    if not capture.isOpened():
        print(f'cannot open video: {args.video}', file=sys.stderr)
        return 1

    ok, frame = capture.read()
    if not ok:
        print('cannot read first frame', file=sys.stderr)
        capture.release()
        return 1

    bbox = cv2.selectROI('track_objects', frame, showCrosshair=False, fromCenter=False)
    if bbox == (0, 0, 0, 0):
        print('no ROI selected', file=sys.stderr)
        capture.release()
        cv2.destroyAllWindows()
        return 1

    tracker = cv2.TrackerMIL_create()
    tracker.init(frame, bbox)

    writer = None
    if args.output:
        fps = capture.get(cv2.CAP_PROP_FPS) or 25.0
        size = (int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)),
                int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        writer = cv2.VideoWriter(str(args.output), cv2.VideoWriter_fourcc(*'mp4v'), fps, size)

    try:
        while True:
            ok, bbox = tracker.update(frame)
            if ok:
                x, y, w, h = (int(v) for v in bbox)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.imshow('track_objects', frame)
            if writer is not None:
                writer.write(frame)
            if cv2.waitKey(30) & 0xFF == ord('q'):
                break
            ok, frame = capture.read()
            if not ok:
                break
    finally:
        capture.release()
        if writer is not None:
            writer.release()
        cv2.destroyAllWindows()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
