from ultralytics import YOLO

model = YOLO("../runs/models/phone_detector-5/weights/best.pt")

results = model.predict(
    source="../datasets/phone_detection_dataset/test/images",
    conf=0.5,
    save=True
)

print("Inference Completed")