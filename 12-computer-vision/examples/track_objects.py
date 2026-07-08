import cv2

tracker = cv2.TrackerCSRT_create()
bbox = (287, 23, 86, 320)
tracker.init(frame, bbox)

while True:
    ok, bbox = tracker.update(frame)
    if ok:
        p1 = (int(bbox[0]), int(bbox[1]))
        p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
        cv2.rectangle(frame, p1, p2, (255, 0, 0), 2)
