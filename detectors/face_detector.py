import cv2
import mediapipe as mp


class FaceDetector:

    def __init__(self):

        self.face_detection = mp.solutions.face_detection.FaceDetection(
            model_selection=0,
            min_detection_confidence=0.6
        )

        self.drawer = mp.solutions.drawing_utils

    def detect(self, frame):

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = self.face_detection.process(rgb)

        face_count = 0
        face_boxes = []

        if results.detections:

            face_count = len(results.detections)

            for detection in results.detections:

                bbox = detection.location_data.relative_bounding_box

                h, w, _ = frame.shape

                x = int(bbox.xmin * w)
                y = int(bbox.ymin * h)
                width = int(bbox.width * w)
                height = int(bbox.height * h)

                face_boxes.append({
                    "bbox": (x, y, width, height)
                })

                self.drawer.draw_detection(frame, detection)

        return {
            "frame": frame,
            "count": face_count,
            "faces": face_boxes
        }