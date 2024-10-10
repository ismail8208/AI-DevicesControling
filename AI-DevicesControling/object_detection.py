import time
import numpy as np
import cv2
from utils import set_result
import logging
from ultralytics import YOLO
# from supervision import Detections
from supervision.tools.detections import Detections

import socket
import time

logging.getLogger('ultralytics').setLevel(logging.ERROR)
model = YOLO('best.pt')
CLASS_NAMES_DICT = model.model.names
url = 'http:192.168.1.5:8000/stream.mjpg'
cap = cv2.VideoCapture(url)
# cap.set(cv2.CAP_PROP_FPS, 24)
def object_detection_worker(stop_event):
    print("object_detection_worker started")
    time.sleep(2)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('127.0.0.1', 8080))
    try :
        while not stop_event.is_set():
            if cap.isOpened():

                for _ in range(10):
                    cap.grab()

                ret, frame = cap.read() 
                if not ret:
                    print("Failed to retrieve frame.")
                    continue
                
                # Resize the frame to 640x480 pixels
                frame = cv2.resize(frame, (640, 640))
                # new_width = int(img.shape[1] * 0.8)
                # new_height = int(img.shape[0] * 0.8)
                # img_resized = cv2.resize(img, (new_width, new_height))
                results = model.track(frame, persist=True, conf=0.10)
                detections = Detections(
                    xyxy=results[0].boxes.xyxy.cpu().numpy(),
                    confidence=results[0].boxes.conf.cpu().numpy(),
                    class_id=results[0].boxes.cls.cpu().numpy().astype(int)
                )
                # if detections.confidence.size > 0:
                #     if detections.confidence[max_conf_index] > 0.50:
                #         best_class_id = detections.class_id[max_conf_index]
                #         best_class_name = CLASS_NAMES_DICT[best_class_id]
                #         message = best_class_name.encode('utf-8')
                #         client_socket.sendall(message)
                if detections.confidence.size > 0 :
                    max_conf_index = np.argmax(detections.confidence)
                    best_class_id = detections.class_id[max_conf_index]
                    # first_confidence = detections.confidence[0]
                    # if first_confidence > 0.50:
                    # first_class_id = detections.class_id[0]
                    # first_class_name = CLASS_NAMES_DICT[first_class_id]
                    # message = first_class_name.encode('utf-8')
                    client_socket.sendall(bytes([best_class_id]))
                    # print(first_class_id)
    except Exception as e:
        print(e)
        client_socket.close()

