from .model import model

YOLO_TO_CATEGORY = {
    "laptop": "Laptop",
    "mouse": "Mouse",
    "keyboard": "Keyboard",
    "tablet": "Tablet",
    "cell phone": "Tablet",
    "monitor": "Monitor",
    "tv": "Monitor",
    "usb-flash-drive": "Accessories",
    "powerbank": "Accessories",
    "gamepad": "Accessories",
    "speak": "Accessories",
    "computer": "Laptop",
    "printer": "Printer"
}
def detect_category(image_path, conf_thres=0.15):
    results = model(image_path, conf=conf_thres, iou=0.45)
    detected = []

    for r in results:
        for box in r.boxes:
            conf = float(box.conf[0])
            cls = int(box.cls[0])
            name = model.names[cls].lower()
            print(conf, name)

            if conf >= conf_thres:
                detected.append(YOLO_TO_CATEGORY[name])

    return list(set(detected))