import os
import sys
import time
import threading

import cv2

# Ensure project root is on sys.path so backend imports work
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from utils.camera           import Camera
from utils.evidence_manager import EvidenceManager
from utils.decision_engine  import DecisionEngine
from utils.report_generator import ReportGenerator
from detectors.face_detector      import FaceDetector
from detectors.phone_detector     import PhoneDetector
from detectors.head_pose_detector import HeadPoseDetector
from frontend.streamer            import MJPEGStreamer


class _SessionReportGenerator(ReportGenerator):
    """Saves reports to the candidate-specific session directory."""
    def __init__(self, evidence_manager, session_start, candidate_name, session_dir):
        super().__init__(evidence_manager, session_start, candidate_name)
        self.reports_dir = session_dir
        os.makedirs(self.reports_dir, exist_ok=True)


class InterviewSession:
    """
    Manages the full interview session.
    AI monitoring runs in a background thread — completely invisible to the candidate.
    A clean (unannotated) frame is exposed for the Streamlit UI.
    """

    def __init__(self, candidate: dict, session_dir: str):
        self.candidate     = candidate
        self.session_dir   = session_dir
        self.session_start = time.time()

        screenshots_dir = os.path.join(session_dir, "screenshots")
        os.makedirs(session_dir, exist_ok=True)

        # Backend — initialised in the calling (main) thread for library safety
        self.camera             = Camera()
        self.evidence_manager   = EvidenceManager()
        self.decision_engine    = DecisionEngine(self.evidence_manager, screenshots_dir)
        self.face_detector      = FaceDetector()
        self.phone_detector     = PhoneDetector()
        self.head_pose_detector = HeadPoseDetector()

        self._running      = False
        self._thread       = None
        self.streamer      = MJPEGStreamer(self.camera, port=8502)

        self._start()

    def _start(self):
        self._running = True
        self.streamer.start()
        self._thread  = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def _loop(self):
        import time
        while self._running:
            t0 = time.time()
            
            # 1. Capture
            frame = self.camera.read()
            if frame is None:
                time.sleep(0.01)
                continue
            
            t1 = time.time()
            capture_ms = (t1 - t0) * 1000

            # 2. Face Detector (MediaPipe)
            face_copy   = frame.copy()
            face_result = self.face_detector.detect(face_copy)
            t2 = time.time()
            face_ms = (t2 - t1) * 1000

            # 3. Phone Detector (YOLO)
            phone_result = self.phone_detector.detect(frame)
            t3 = time.time()
            phone_ms = (t3 - t2) * 1000

            # 4. Head Pose (MediaPipe)
            pose_result  = self.head_pose_detector.detect(frame)
            t4 = time.time()
            pose_ms = (t4 - t3) * 1000

            # 5. Annotation & Decision
            annot = face_copy
            for phone in phone_result.get("phones", []):
                x1, y1, x2, y2 = phone["bbox"]
                cv2.rectangle(annot, (x1, y1), (x2, y2), (0, 0, 255), 2)

            self.decision_engine.observe(face_result, phone_result, pose_result, annot)

            # Sleep briefly to yield CPU, then grab the *next* newest frame
            time.sleep(0.01)

    def get_frame(self):
        """Return the latest clean camera frame (no detection overlays) directly from the camera thread."""
        return self.camera.read()

    def stop(self):
        self._running = False
        
        # Release the camera FIRST. This breaks the streamer loop.
        self.camera.release()
        
        # Now the streamer can safely shut down without deadlocking.
        self.streamer.stop()
        
        if self._thread:
            self._thread.join(timeout=3)

    def generate_reports(self) -> dict:
        gen = _SessionReportGenerator(
            self.evidence_manager,
            self.session_start,
            self.candidate.get("name", "Unknown"),
            self.session_dir
        )
        gen.generate()
        return {
            "json_path": os.path.join(self.session_dir, "report.json"),
            "pdf_path":  os.path.join(self.session_dir, "report.pdf"),
        }
