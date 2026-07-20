import cv2
from ultralytics import YOLO


# ==========================
# Load Trained Model
# ==========================
model = YOLO("models/phone_detector/best.pt")   # Change path if needed


# ==========================
# Open Webcam
# ==========================
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Could not open webcam.")
    exit()


print("Phone Detector Started")
print("Press Q to Quit")


while True:

    ret, frame = cap.read()

    if not ret:
        break

    # Mirror image
    frame = cv2.flip(frame, 1)

    # Run inference
    results = model(
        frame,
        conf=0.80,      # Increase if getting false positives
        verbose=False
    )

    phone_detected = False

    for result in results:

        for box in result.boxes:

            phone_detected = True

            x1, y1, x2, y2 = map(int, box.xyxy[0])

            confidence = float(box.conf[0])

            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                (0, 0, 255),
                2
            )

            cv2.putText(
                frame,
                f"Phone {confidence:.2f}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2
            )

    # Display Status
    if phone_detected:
        status = "PHONE DETECTED"
        color = (0, 0, 255)
    else:
        status = "NO PHONE"
        color = (0, 255, 0)

    cv2.putText(
        frame,
        status,
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        color,
        3
    )

    cv2.imshow("Phone Detector Test", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break


cap.release()
cv2.destroyAllWindows()