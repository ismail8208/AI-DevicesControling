import io
import logging
import socketserver
from threading import Condition, Thread
from http import server
import cv2
import time

PAGE = """\
<html>
<head>
<title>Webcam Stream</title>
</head>
<body>
<center><h1>Webcam Stream</h1></center>
<center><img src="stream.mjpg" width="640" height="480"></center>
</body>
</html>
"""


class StreamingOutput(object):
    def _init_(self):
        self.frame = None
        self.condition = Condition()

    def set_frame(self, frame):
        with self.condition:
            self.frame = frame
            self.condition.notify_all()


class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    if frame:
                        self.wfile.write(b'--FRAME\r\n')
                        self.send_header('Content-Type', 'image/jpeg')
                        self.send_header('Content-Length', len(frame))
                        self.end_headers()
                        self.wfile.write(frame)
                        self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


def capture_frames(output):
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)  # Set the FPS (Frames Per Second)

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        # Optimized JPEG encoding
        ret, jpeg = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
        if not ret:
            continue

        output.set_frame(jpeg.tobytes())

        # Sleep to match the desired frame rate
        # time.sleep(0.03)  # 30 FPS


if _name_ == '_main_':
    output = StreamingOutput()
    capture_thread = Thread(target=capture_frames, args=(output,))
    capture_thread.daemon = True
    capture_thread.start()

    address = ('', 8000)
    server = StreamingServer(address, StreamingHandler)
    server.serve_forever()