import cv2
import threading
import time

class Camera:
    """
    Handles webcam operations.
    Runs completely in a background thread to prevent OpenCV buffer lag.
    """

    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.latest_frame = None
        self.running = True
        self.lock = threading.Lock()
        
        # Start background capture thread
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()

        # Wait until we have at least one frame before returning
        while self.latest_frame is None and self.running:
            time.sleep(0.01)

    def _capture_loop(self):
        # IMPORTANT FIX: Initialize VideoCapture IN THE SAME THREAD that reads it!
        # Windows DirectShow will deadlock if initialized in main thread and read in a sub-thread.
        cap = cv2.VideoCapture(self.camera_index)
        if not cap.isOpened():
            self.running = False
            return
            
        while self.running:
            success, frame = cap.read()
            if success:
                frame = cv2.flip(frame, 1)
                with self.lock:
                    self.latest_frame = frame
            else:
                time.sleep(0.01)
                
        # Release the camera inside the thread when running is False
        cap.release()

    def read(self):
        """Returns the most recent frame instantly (non-blocking)."""
        with self.lock:
            if self.latest_frame is not None:
                return self.latest_frame.copy()
            return None

    def release(self):
        self.running = False
        if self.thread.is_alive():
            self.thread.join(timeout=1.0)