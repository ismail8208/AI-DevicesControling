import ctypes
import multiprocessing
from multiprocessing import Process, Event, Queue
from capture_frame import capture_frames
from object_detection import object_detection_worker
from hand_gesture_recognition import hand_gesture_recognition_worker
from RaspberryPiSender import RaspberryPiSender
from utils import IMAGE_WIDTH, IMAGE_HEIGHT

def main():

    # RaspberryPiSender_Queue = multiprocessing.Queue(maxsize=1)

    stop_event = Event()
    hand_gesture_process = multiprocessing.Process(target=hand_gesture_recognition_worker, args=(stop_event,), daemon=True)
    object_detection_process = multiprocessing.Process(target=object_detection_worker, args=(stop_event,), daemon=True)
    # RaspberryPi_sender = multiprocessing.Process(target=RaspberryPiSender, args=(RaspberryPiSender_Queue, stop_event,), daemon=True)

    object_detection_process.start()
    hand_gesture_process.start()
    # RaspberryPi_sender.start()

    try:
        object_detection_process.join()
        hand_gesture_process.join()
        # RaspberryPi_sender.join()
    except KeyboardInterrupt:
        stop_event.set()

if __name__ == '__main__':
    main()
