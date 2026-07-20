import time
import cv2

from utils.camera import Camera
from utils.evidence_manager import EvidenceManager
from utils.decision_engine import DecisionEngine
from utils.report_generator import ReportGenerator
from detectors.face_detector import FaceDetector
from detectors.phone_detector import PhoneDetector
from detectors.head_pose_detector import HeadPoseDetector

# ─────────────────────────────────────
# Initialise
# ─────────────────────────────────────

camera = Camera()

session_start    = time.time()
evidence_manager = EvidenceManager()
decision_engine  = DecisionEngine(evidence_manager)
face_detector    = FaceDetector()
phone_detector   = PhoneDetector()
head_pose_detector = HeadPoseDetector()

print("AI Interview Proctor Started")
print("Press Q to Quit")

# ─────────────────────────────────────
# Main Loop
# ─────────────────────────────────────

while True:

    frame = camera.read()

    if frame is None:
        break

    # ── Take one clean copy before any drawing ──
    clean = frame.copy()

    # ────────────────────────────────────────────
    # Detection Phase  (all detectors use 'clean')
    # ────────────────────────────────────────────

    # Face detection — draws landmarks on 'frame' in-place
    face_result = face_detector.detect(frame)

    frame = face_result["frame"]
    face_count = face_result["count"]

    # Phone detection — YOLO sees the untouched clean frame
    phone_result   = phone_detector.detect(clean)
    phones         = phone_result["phones"]
    phone_detected = phone_result["detected"]

    # Head pose — FaceMesh also sees the untouched clean frame
    pose_result = head_pose_detector.detect(clean)

    # ────────────────────────────────────────────
    # Drawing Phase  (everything drawn on 'frame')
    # ────────────────────────────────────────────

    # ── Phone boxes ───────────────────────────
    for phone in phones:

        x1, y1, x2, y2 = phone["bbox"]
        confidence      = phone["confidence"]

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)

        cv2.putText(
            frame,
            f"Phone {confidence:.2f}",
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 0, 255),
            2
        )

    # ── Status labels (top-left) ──────────────
    phone_text  = "Detected"  if phone_detected else "Not Detected"
    phone_color = (0, 0, 255) if phone_detected else (0, 255, 0)

    cv2.putText(
        frame,
        f"Faces : {face_count}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2
    )

    cv2.putText(
        frame,
        f"Ph {phone_text}",
        (20, 75),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        phone_color,
        2
    )

    # ── Head pose status ───────────────────────
    if pose_result["yaw"] is not None:

        pose_alerts = pose_result["alerts"]
        pose_color  = (0, 0, 255) if pose_alerts else (0, 255, 0)
        pose_text   = pose_alerts[0] if pose_alerts else "Head Pose: NORMAL"

        cv2.putText(
            frame,
            pose_text,
            (20, 110),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            pose_color,
            2
        )

        # Show angle readout in smaller text below
        # cv2.putText(
        #     frame,
        #     f"Y:{pose_result['yaw']:+.1f}  P:{pose_result['pitch']:+.1f}  R:{pose_result['roll']:+.1f}",
        #     (20, 140),
        #     cv2.FONT_HERSHEY_SIMPLEX,
        #     0.55,
        #     (200, 200, 200),
        #     1
        # )

    # ── Behaviour state + event count ─────────────
    total   = decision_engine.get_total_events()
    highest = decision_engine.get_highest_state()
    state_colors = {
        "NORMAL":      (200, 200, 200),
        "OBSERVATION": (255, 255,   0),
        "SUSPICIOUS":  (  0, 165, 255),
        "WARNING":     (  0,  80, 255),
        "VIOLATION":   (  0,   0, 220),
    }
    cv2.putText(
        frame,
        f"State: {highest}   Events: {total}",
        (20, 175),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        state_colors.get(highest, (200, 200, 200)),
        2
    )

    # observe() is called here so screenshots include all visual overlays
    decision_engine.observe(face_result, phone_result, pose_result, frame)

    # ── Footer ────────────────────────────────
    cv2.putText(
        frame,
        "Press Q to Quit",
        (20, frame.shape[0] - 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2
    )

    cv2.imshow("AI Interview Proctor", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ─────────────────────────────────────
# Cleanup
# ─────────────────────────────────────

camera.release()
cv2.destroyAllWindows()
ReportGenerator(evidence_manager, session_start).generate()