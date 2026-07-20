import cv2
import time
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""
    daemon_threads = True  # CRITICAL: Ensures sockets do not block app exit!

class MJPEGStreamer:
    """
    A lightweight, dedicated HTTP server that streams the webcam feed natively to the browser.
    This eliminates Streamlit rendering overhead and allows a zero-latency video feed.
    """
    def __init__(self, camera, port=8502):
        self.camera = camera
        self.port = port
        self.server = None
        self.thread = None

    def start(self):
        camera = self.camera

        class CamHandler(BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                # Suppress http.server logging to keep the terminal clean
                pass

            def do_GET(self):
                if self.path == '/video_feed':
                    self.send_response(200)
                    self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=frame')
                    # CORS headers so Streamlit can embed it smoothly
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    
                    try:
                        while getattr(camera, 'running', False):
                            frame = camera.read()
                            if frame is not None:
                                ret, jpeg = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
                                if ret:
                                    self.wfile.write(b'--frame\r\n')
                                    self.send_header('Content-Type', 'image/jpeg')
                                    self.send_header('Content-Length', str(len(jpeg)))
                                    self.end_headers()
                                    self.wfile.write(jpeg.tobytes())
                                    self.wfile.write(b'\r\n')
                            time.sleep(0.033)  # ~30fps cap
                    except Exception:
                        pass # Client disconnected or camera closed
                else:
                    self.send_response(404)
                    self.end_headers()

        self.server = ThreadedHTTPServer(('0.0.0.0', self.port), CamHandler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def stop(self):
        if self.server:
            self.server.shutdown()
            self.server.server_close()
        if self.thread:
            self.thread.join(timeout=1.0)
