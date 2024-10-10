from enum import Enum


IMAGE_WIDTH = 640
IMAGE_HEIGHT = 480

def set_result(queue, result):
    queue.put(result)
    

def get_result(queue):
    if not queue.empty():
        return queue.get()
    
def read_deque(queue):
    if queue :
        temp = queue.popleft()
        queue.append(temp)
        return temp

def get_deque(queue):
     if queue :
        return queue.popleft()

class ObjectType(Enum):
    Lamp = 1
    Motor = 2
    Unknown = 3

class Decision:
    def __init__(self, number: int, type: ObjectType):
        self.number = number
        self.type = type
