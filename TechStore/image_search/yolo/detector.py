from .model import model

YOLO_TO_CATEGORY = {
    "laptop": "Laptop",
    "mouse": "Mouse",
    "keyboard": "Keyboard",
    "cell phone": "Tablet",
    "tv": "Monitor",
}

def detect_category(image_path, conf_thres=0.4):
    results = model(image_path)
    detected = []

    for r in results:
        for box in r.boxes:
            conf = float(box.conf[0])
            cls = int(box.cls[0])
            name = model.names[cls]

            if conf >= conf_thres and name in YOLO_TO_CATEGORY:
                detected.append(YOLO_TO_CATEGORY[name])

    return list(set(detected))