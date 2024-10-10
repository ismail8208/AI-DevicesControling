import cv2
import time
import numpy as np
import HandTrackingModule as htm
from utils import ObjectType, Decision
import socket
import threading
import queue
from enum import Enum
from collections import deque

pTime = 0

detector = htm.handDetector(detectionCon=0.7, maxHands=1)

Bar = 400
percent = 0
area = 0
color = (255, 0, 0)
decision_queue = queue.Queue()
detection_decision = deque(maxlen=2)

# def send_decision():
#     if not decision_queue.empty():
#         decision = decision_queue.get()
#         print(decision.type)
   
#     try:
#         while True:
#             if not decision_queue.empty() :
#                 decision = decision_queue.get()
#                 print(decision.type)
#                 if decision.type == ObjectType.Lamp:
#                     if decision.number < 50:
#                         message = str(-1)
#                         print(message)
#                     else :
#                         message = str(101)
#                         print(message)
#                     client_socket.send(message.encode('utf-8'))

#                 elif decision.type == ObjectType.Motor:
#                     message = str(decision.number)
   
#                     client_socket.send(message.encode('utf-8'))
#     except Exception as e:
#         print(e)
#     finally:
#         client_socket.close()

def decision_maker(gestures_detected, objects_detected, client_socket):
    decision = Decision(gestures_detected, ObjectType[objects_detected])
    if decision.type == ObjectType.Lamp:
        if decision.number < 50:
            message = str(-1)
            print(message)
        else :
            message = str(101)
            print(message)
        client_socket.send(message.encode('utf-8'))

    elif decision.type == ObjectType.Motor:
        message = str(decision.number)

        client_socket.send(message.encode('utf-8'))
    # if not RaspberryPiSender_Queue.full():
    #     RaspberryPiSender_Queue.put(decision)


def draw_circle(img, center, color):
    cv2.circle(img, center, 15, color, cv2.FILLED)

url = 'http:192.168.1.5:8000/stream.mjpg'
cap = cv2.VideoCapture(url)

def start_server(server_socket, detection_decision, stop_event):
    server_socket.listen(1)
    print("Server is listening on port 8080...")
    conn, addr = server_socket.accept()
    print(f"Connection established with {addr}")
    try:
        while not stop_event.is_set():
            data = conn.recv(1)
            if data:
                value = int.from_bytes(data, byteorder='big')
                if not detection_decision :
                    detection_decision.append(value)
    except Exception as e:
         print(f"Server error: {e}")
    finally:
        conn.close()
        server_socket.close()

def hand_gesture_recognition_worker(stop_event):
    print("hand_gesture_recognition_worker started")
    # decision_thread = threading.Thread(target=send_decision, daemon=True)
    # decision_thread.setDaemon(True)
    # decision_thread.start()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 8080))

    raspberry_pi_ip = '192.168.1.3'
    port = 8000
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((raspberry_pi_ip, port))
    objects_detected = ""
    c = 0
    is_new_value = False

    threading.Thread(target=start_server, args=(server_socket, detection_decision, stop_event), daemon=True).start()

    while not stop_event.is_set():
        if cap.isOpened():
            _, img = cap.read()
            gestures_detected = perform_hand_gesture_recognition(img)

            if detection_decision:
                detectedValue = detection_decision.popleft()
                if detectedValue == 0:
                    objects_detected = "Lamp"
                    is_new_value = True
                elif detectedValue == 1:
                    objects_detected = "Motor"
                    is_new_value = True

            cv2.putText(img, objects_detected, (280, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

            cv2.imshow('Captured Frame', img)
            key = cv2.waitKey(1)

            if key & 0xFF == ord('q'):
                stop_event.set()

            elif key &  0xFF == ord('r'):
                decision_maker(0, "Lamp", client_socket)
                decision_maker(0, "Motor", client_socket)

            elif key &  0xFF == ord('m'):
                decision_maker(0, "Motor", client_socket)

            elif key &  0xFF == ord('l'):
                decision_maker(0, "Lamp", client_socket)

            if gestures_detected != -500 and objects_detected:
                decision_maker(gestures_detected, objects_detected, client_socket)
            # objects_detected = get_result(object_detection_result)

            if is_new_value:
                c = 0
                is_new_value = False

            if (c == 30):   
                objects_detected = ""
                c = 0  

            c = c + 1

def perform_hand_gesture_recognition(frame):
    try:
        global pTime
        result = -500
        Bar = 400
        img = detector.findHands(frame)
        lmList, bbox = detector.findPosition(img, draw=True)
        if len(lmList) != 0:
            area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1]) // 100
            if 300 < area < 1000:
                lengthIndexThump, img, lineInfo = detector.findDistance(4, 8, img)
                handLength, _, _ = detector.findDistance(0, 12, img, False)
                value = (lengthIndexThump / handLength) * 400
                Bar = np.interp(value, [50, 200], [400, 150])
                percent = np.interp(value, [50, 200], [0, 100])
                smoothness = 10
                percent = smoothness * round(percent / smoothness)
                result = percent
                #result =  percent if not detector.are_pinky_ring_middle_raised() else -500
                #print(detector.are_pinky_ring_middle_raised())
                # if not fingers[3] and not fingers[4]:
                #     if percent < 50:
                #         result = -1
                #     else:
                #         result = 101
                #     draw_circle(img, (lineInfo[4], lineInfo[5]), (0, 0, 255))
                # elif not fingers[4]:
                #     result = percent
                #     draw_circle(img, (lineInfo[4], lineInfo[5]), (0, 255, 0))

                    # results = model.track(img, persist=True)

        result_as_string = 0 if result == -500 else result
        # Drawings
        cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3)
        cv2.rectangle(img, (50, int(Bar)), (85, 400), (255, 0, 0), cv2.FILLED)
        cv2.putText(img, f'{int(result_as_string)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX,
                    1, (255, 0, 0), 3)

        # Frame rate
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(img, f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_COMPLEX,
                    1, (255, 0, 0), 3)
        return result
    except Exception as e:
        print(f"Error in hand gesture recognition: {e}")
        return 0
