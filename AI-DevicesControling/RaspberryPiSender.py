import time
import numpy as np
import cv2
import socket
from utils import ObjectType


def RaspberryPiSender(RaspberryPiSender_Queue ,stop_event):
    raspberry_pi_ip = '192.168.1.3'
    port = 8000
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((raspberry_pi_ip, port))

    try:
        while not stop_event.is_set():
            if not RaspberryPiSender_Queue.empty() :
                decision = RaspberryPiSender_Queue.get()
                print("From RaspberryPiSender", decision.type)
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
                    print(message)
                    client_socket.send(message.encode('utf-8'))
    except Exception as e:
        print(e)
    finally:
        client_socket.close()