import cv2
import socket
import struct
import pickle
import threading
import time

url = 'http:192.168.1.5:8000/stream.mjpg'

def capture_and_send_frames(server_ip, server_port, stop_event):
    cap = cv2.VideoCapture(url)

    # cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    # cap.set(cv2.CAP_PROP_FPS, 10)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, server_port))

    while cap.isOpened() and not stop_event.is_set():
        ret, img = cap.read()
        if not ret:
            break
        
        data = pickle.dumps(img)
        size = len(data)
        
        client_socket.sendall(struct.pack(">L", size) + data)
    cap.release()
    client_socket.close()

if __name__ == "__main__":
    stop_event = threading.Event()
    server_ip = '127.0.0.1'
    server_port = 9999

    capture_thread = threading.Thread(target=capture_and_send_frames, args=(server_ip, server_port, stop_event))
    capture_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_event.set()
        capture_thread.join()
