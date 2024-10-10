import cv2
import numpy as np
from utils import IMAGE_WIDTH, IMAGE_HEIGHT
url = 'http:192.168.1.5:8000/stream.mjpg'
def capture_frames(frame_queue, stop_event):
    cap = cv2.VideoCapture(0)
    # cap.set(cv2.CAP_PROP_FRAME_WIDTH, IMAGE_WIDTH)
    # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, IMAGE_HEIGHT)
    # cap.set(cv2.CAP_PROP_FPS, 10)
    while cap.isOpened() and not stop_event.is_set():
        ret, img = cap.read()
        if not ret:
            break
        if not frame_queue.full():
            frame_queue.put(img)
    cap.release()
    cv2.destroyAllWindows()