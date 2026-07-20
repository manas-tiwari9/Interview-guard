import os
import time
import cv2
from datetime import datetime

from utils.behaviour_tracker import BehaviourTracker
from utils.evidence_manager import EvidenceManager


# Edit thresholds here to tune sensitivity (all values in seconds)
THRESHOLDS = {
    "LOOKING_AWAY": {
        "observation": 1.0, "suspicious": 3.0, "warning": 5.0, "violation": 8.0
    },
    "PHONE_VISIBLE": {
        "observation": 1.0, "suspicious": 3.0, "warning": 6.0, "violation": 12.0
    },
    "PHONE_WHILE_LOOKING_DOWN": {   # compound: phone detected AND head looking down
        "observation": 0.5, "suspicious": 2.0, "warning": 4.0, "violation": 6.0
    },
    "NO_FACE": {
        "observation": 1.0, "suspicious": 3.0, "warning": 5.0, "violation": 10.0
    },
    "MULTIPLE_FACES": {
        "observation": 0.5, "suspicious": 2.0, "warning": 3.0, "violation": 5.0
    },
}

_DESCRIPTIONS = {
    "LOOKING_AWAY":            "Candidate looked {direction} continuously for {duration:.1f} seconds.",
    "PHONE_VISIBLE":           "Phone remained visible for {duration:.1f} seconds.",
    "PHONE_WHILE_LOOKING_DOWN":"Phone visible while candidate looked downward for {duration:.1f} seconds.",
    "NO_FACE":                 "No face detected for {duration:.1f} seconds.",
    "MULTIPLE_FACES":          "{face_count} faces detected simultaneously for {duration:.1f} seconds.",
}

_STATE_PRIORITY = ["VIOLATION", "WARNING", "SUSPICIOUS", "OBSERVATION", "NORMAL"]


class DecisionEngine:
    """
    Intelligent behaviour analysis engine.
    Observes detector outputs over time and only creates evidence when a
    behaviour crosses WARNING or VIOLATION thresholds — brief fluctuations
    are silently ignored.
    """

    def __init__(self, evidence_manager: EvidenceManager,
                 screenshots_dir: str = "reports/screenshots"):
        self.evidence_manager = evidence_manager
        self.screenshots_dir  = screenshots_dir
        os.makedirs(screenshots_dir, exist_ok=True)

        self._trackers = {
            name: BehaviourTracker(t) for name, t in THRESHOLDS.items()
        }
        self._total_events = 0

    def observe(self, face_result: dict, phone_result: dict,
                pose_result: dict, frame=None):
        """
        Call once per frame after all drawings are applied to `frame`.
        Screenshots are taken here so they include all visual overlays.
        """
        now    = time.time()
        phone  = phone_result["detected"]
        faces  = face_result["count"]
        status = pose_result["status"]

        conditions = {
            "LOOKING_AWAY":            status not in ("NORMAL", "NO_FACE"),
            "PHONE_VISIBLE":           phone,
            "PHONE_WHILE_LOOKING_DOWN":phone and status == "DOWN",
            "NO_FACE":                 faces == 0,
            "MULTIPLE_FACES":          faces > 1,
        }

        for behaviour, is_active in conditions.items():
            tracker = self._trackers[behaviour]
            signal  = tracker.observe(is_active, now)

            # Only create evidence at WARNING / VIOLATION — nothing below that is logged
            if signal == "ESCALATED" and tracker.state in ("WARNING", "VIOLATION"):
                self._create_evidence(
                    behaviour, tracker, face_result, phone_result, pose_result, frame
                )

    def _create_evidence(self, behaviour, tracker, face_result,
                         phone_result, pose_result, frame):
        screenshot = None
        if frame is not None:
            ts       = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"{ts}_{behaviour}_{tracker.state}.jpg"
            path     = os.path.join(self.screenshots_dir, filename)
            cv2.imwrite(path, frame)
            screenshot = path

        description = _DESCRIPTIONS.get(
            behaviour, "Suspicious behaviour for {duration:.1f} seconds."
        ).format(
            duration   = tracker.elapsed,
            direction  = pose_result.get("status", "").lower(),
            face_count = face_result.get("count", 0)
        )

        meta = {}
        if behaviour in ("LOOKING_AWAY", "PHONE_WHILE_LOOKING_DOWN"):
            meta.update(
                direction = pose_result.get("status"),
                yaw       = pose_result.get("yaw"),
                pitch     = pose_result.get("pitch")
            )
        if behaviour in ("PHONE_VISIBLE", "PHONE_WHILE_LOOKING_DOWN"):
            meta["phone_count"] = len(phone_result.get("phones", []))
        if behaviour in ("NO_FACE", "MULTIPLE_FACES"):
            meta["face_count"] = face_result.get("count", 0)

        self.evidence_manager.add_evidence(
            event_type  = behaviour,
            description = description,
            duration    = round(tracker.elapsed, 1),
            state       = tracker.state,
            metadata    = meta,
            screenshot  = screenshot
        )
        self._total_events += 1

    def get_current_states(self) -> dict:
        return {name: t.state for name, t in self._trackers.items()}

    def get_highest_state(self) -> str:
        states = self.get_current_states()
        for s in _STATE_PRIORITY:
            if any(v == s for v in states.values()):
                return s
        return "NORMAL"

    def get_total_events(self) -> int:
        return self._total_events
