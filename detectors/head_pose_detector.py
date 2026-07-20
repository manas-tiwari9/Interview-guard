import cv2
import mediapipe as mp
import numpy as np


class HeadPoseDetector:
    """
    Detects head pose (yaw, pitch, roll) using MediaPipe FaceMesh
    and OpenCV solvePnP.

    Returns Euler angles and raises alerts when the person
    looks away, up, down, or tilts their head.
    """

    # ──────────────────────────────────────────────
    # 3D reference points of a generic face model (mm)
    # These correspond to the FaceMesh landmark IDs below
    # ──────────────────────────────────────────────
    MODEL_POINTS = np.array([
        (0.0,    0.0,    0.0),        # Nose tip
        (0.0,  -330.0,  -65.0),       # Chin
        (-225.0,  170.0, -135.0),     # Left eye outer corner
        ( 225.0,  170.0, -135.0),     # Right eye outer corner
        (-150.0, -150.0, -125.0),     # Left mouth corner
        ( 150.0, -150.0, -125.0),     # Right mouth corner
    ], dtype=np.float64)

    # Matching FaceMesh landmark indices
    LANDMARK_IDS = [1, 152, 263, 33, 287, 57]

    # ──────────────────────────────────────────────
    # Alert thresholds (degrees)
    # Calibrated from real data:
    #   Normal position sits at ~Yaw+11, Pitch+8, Roll+2
    #   Suspicious turns reach Yaw±60-70, Pitch±32-52
    # ──────────────────────────────────────────────
    YAW_THRESHOLD   = 35    # left / right — catches ±60-70° turns, ignores natural ±11° offset
    PITCH_THRESHOLD = 25    # up / down   — catches ±32-52°,  ignores natural +8° offset
    ROLL_THRESHOLD  = 25    # sideways tilt (only checked when NOT in gimbal lock zone)

    def __init__(self):

        self.face_mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    def detect(self, frame):
        """
        Parameters
        ----------
        frame : np.ndarray
            Clean BGR frame (must be unannotated).

        Returns
        -------
        angles : dict or None
            {"yaw": float, "pitch": float, "roll": float}
            None if no face is found.

        alerts : list[str]
            Active movement alerts e.g. ["Looking LEFT", "Looking DOWN"]
        """

        h, w = frame.shape[:2]

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb)

        if not results.multi_face_landmarks:
            return {
                "status": "NO_FACE",
                "alerts": [],
                "yaw"   : None,
                "pitch" : None,
                "roll"  : None
            }

        landmarks = results.multi_face_landmarks[0].landmark

        # ── 2D image points from FaceMesh ─────────
        image_points = np.array([
            (landmarks[idx].x * w, landmarks[idx].y * h)
            for idx in self.LANDMARK_IDS
        ], dtype=np.float64)

        # ── Approximate camera matrix ──────────────
        focal_length  = w
        camera_matrix = np.array([
            [focal_length, 0,            w / 2],
            [0,            focal_length, h / 2],
            [0,            0,            1    ]
        ], dtype=np.float64)

        dist_coeffs = np.zeros((4, 1), dtype=np.float64)

        # ── Solve PnP ─────────────────────────────
        success, rvec, tvec = cv2.solvePnP(
            self.MODEL_POINTS,
            image_points,
            camera_matrix,
            dist_coeffs,
            flags=cv2.SOLVEPNP_ITERATIVE
        )

        if not success:
            return {
                "status": "NO_FACE",
                "alerts": [],
                "yaw"   : None,
                "pitch" : None,
                "roll"  : None
            }

        # ── Rotation vector → Euler angles ────────
        rmat, _ = cv2.Rodrigues(rvec)
        angles, _, _, _, _, _ = cv2.RQDecomp3x3(rmat)

        pitch = angles[0]   # up / down
        yaw   = angles[1]   # left / right
        roll  = angles[2]   # tilt

        # ── Build alerts ──────────────────────────
        alerts = []

        if yaw > self.YAW_THRESHOLD:
            alerts.append("Looking RIGHT")
        elif yaw < -self.YAW_THRESHOLD:
            alerts.append("Looking LEFT")

        if pitch > self.PITCH_THRESHOLD:
            alerts.append("Looking DOWN")
        elif pitch < -self.PITCH_THRESHOLD:
            alerts.append("Looking UP")

        # Roll near ±180° is a gimbal lock artifact (happens during hard left/right/down turns)
        # Only flag a real head tilt when roll is in the safe zone (between -90° and +90°)
        if abs(roll) < 90 and abs(roll) > self.ROLL_THRESHOLD:
            alerts.append("Head TILTED")

        # ── Derive single status string from alerts ────────
        if not alerts:
            status = "NORMAL"
        elif "Looking RIGHT" in alerts:
            status = "RIGHT"
        elif "Looking LEFT" in alerts:
            status = "LEFT"
        elif "Looking DOWN" in alerts:
            status = "DOWN"
        elif "Looking UP" in alerts:
            status = "UP"
        elif "Head TILTED" in alerts:
            status = "TILTED"
        else:
            status = "AWAY"

        return {
            "status": status,
            "alerts": alerts,
            "yaw"   : round(yaw,   2),
            "pitch" : round(pitch, 2),
            "roll"  : round(roll,  2)
        }
