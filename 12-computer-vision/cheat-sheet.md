# Cheat Sheet 12: Комп’ютерний зір на борту

- `cv2.dnn.readNetFromONNX("yolov8n.onnx")`
- `blobFromImage(frame, 1/255, (640,640), swapRB=True, crop=False)`
- `cv2.dnn.NMSBoxes(xywh, scores, 0.4, 0.5)`
- `cv2.VideoCapture("rtsp://...")` + reconnect loop
- `trtexec --onnx=model.onnx --fp16` (Jetson)
