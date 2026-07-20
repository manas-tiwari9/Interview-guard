from ultralytics import YOLO

def main():

    model = YOLO("yolov8n.yaml")

    model.train(
        data="../datasets/phone_detection_dataset/data.yaml",
        epochs=100,
        imgsz=640,
        batch=8,
        device=0,
        workers=2,
        project="../models",
        name="phone_detector",
        pretrained=False,
        patience=20,
        save=True,
        plots=True,
    )


if __name__ == "__main__":
    main()