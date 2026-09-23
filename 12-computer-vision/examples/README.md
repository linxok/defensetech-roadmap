# Приклади 12: Комп’ютерний зір на борту

У `examples/` — спрощена детекція OpenCV DNN (`yolo_opencv.py`) і трекінг (`track_objects.py`). Еталон із тестами: `solution/detection.py`.

Запуск: `pip install -r requirements.txt` (venv репозиторію); `ultralytics` потрібен лише для експорту ONNX.

## Трекінг

```bash
python track_objects.py --video path/to/video.mp4
python track_objects.py --video 0 --output tracked.mp4
```

Приклад використовує `cv2.TrackerMIL_create()`: у opencv-python 4.10 `cv2.TrackerCSRT_create()` відсутній в основному namespace, тому MIL — переносимий варіант. Після відкриття відео виділіть рамку мишею, вихід — клавіша `q`.
