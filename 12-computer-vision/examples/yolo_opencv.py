import cv2
import numpy as np

net = cv2.dnn.readNetFromONNX("yolov8n.onnx")
cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()
    if not ret:
        break
    blob = cv2.dnn.blobFromImage(frame, 1/255.0, (640, 640), swapRB=True)
    net.setInput(blob)
    outputs = net.forward()
    cv2.imshow("detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
