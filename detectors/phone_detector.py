from pathlib import Path
from ultralytics import YOLO


class PhoneDetector:

    def __init__(self):

        # Project Root
        BASE_DIR = Path(__file__).resolve().parent.parent

        # Model Path
        MODEL_PATH = BASE_DIR / "models" / "phone_detector" / "best.pt"

        self.model = YOLO(str(MODEL_PATH))

    def detect(self, frame):

        results = self.model(frame, verbose=False, conf=0.40)

        phones = []

        for box in results[0].boxes:

            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            confidence = float(box.conf[0])

            phones.append({
                "bbox": (x1, y1, x2, y2),
                "confidence": confidence
            })

        return {
            "detected":len(phones)>0,
            "phones":phones
        }