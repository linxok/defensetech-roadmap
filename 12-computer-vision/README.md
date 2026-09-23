# 12. Комп’ютерний зір на борту

> Статус: outline

Побудувати конвеєр детекції з відео: OpenCV + YOLO, коректна постобробка, трекінг і підготовка до edge-інференсу.

## Що потрібно зрозуміти

- YOLOv8 через ONNX у OpenCV DNN: вхід 640×640, letterbox-масштабування без спотворення пропорцій, вихід (1, 84, 8400).
- Постобробка: декодування xywh → xyxy, поріг впевненості, NMS (`cv2.dnn.NMSBoxes` приймає xywh, не xyxy).
- Відео-конвеєр: RTSP/WebRTC для потоку, GStreamer для апаратного декодування на Jetson (`nvv4l2decoder`).
- Edge-інференс: ONNX Runtime або TensorRT; FP16/INT8 квантизація дає 2–4× прискорення ціною точності.
- Трекінг (ByteTrack/DeepSORT) перетворює детекції у траєкторії з ID — саме це потрібно для наведення і підрахунку об’єктів.
- Метрики: mAP@50, FPS, latency p95, споживання GPU/RAM; без замірів «оптимізація» — це вгадування.
- Геоприв’язка: піксель → промінь через калібрування камери → перетин із площиною землі; похибка росте з висотою.

## Контрольні питання

1. Чому NMS отримує рамки у форматі xywh?
2. Як letterbox впливає на координати детекцій?
3. Які метрики доводять, що конвеєр встигає в реальному часі?
4. Що дає TensorRT проти ONNX Runtime на Jetson?
5. Як оцінити відстань до об’єкта без лідара?

## Очікуваний результат

Детектор із чистою постобробкою під тестами (`solution/detection.py`) і виміряний FPS.

## Зв'язок з capstone

Крок 12: CV-сервіс підключається до capstone як споживач відео та публікує детекції в чергу.

## Типові помилки

- Плутати xywh і xyxy у NMS — рамки зникають або дублюються
- Масштабувати координати без урахування letterbox-падінгу
- Пускати інференс у тому ж потоці, що й захоплення кадрів
- Вимірювати FPS без попереднього прогріву моделі

## Первинні джерела

- [OpenCV DNN](https://docs.opencv.org/4.x/d6/d0f/group__dnn.html) — readNetFromONNX, blobFromImage, NMSBoxes
- [Ultralytics Docs](https://docs.ultralytics.com/) — YOLO, export, тренування
- [ONNX Runtime](https://onnxruntime.ai/docs/) — інференс на CPU/GPU
- [NVIDIA Jetson: TensorRT](https://developer.nvidia.com/tensorrt) — квантизація і прискорення
- [GStreamer](https://gstreamer.freedesktop.org/documentation/) — RTSP, апаратне декодування

## Куди далі

Далі: `lab.md` → `detailed-guide.md` → `checklist.md`.
