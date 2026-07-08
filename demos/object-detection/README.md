# Object Detection Demo

Запуск YOLO для детекції об'єктів у відеофайлі або з веб-камери.

## Встановлення

```bash
pip install ultralytics opencv-python
```

## Запуск

```bash
python detect.py --source video.mp4 --output out.mp4
```

## Опції

- `--source`: шлях до відео або `0` для веб-камери.
- `--model`: `yolov8n.pt`, `yolov8s.pt` тощо.
- `--output`: шлях для збереження результату.
