import torch
import numpy as np
from PIL import Image
import open_clip

from image_search.yolo.model import model  # YOLOv8m instance


# Device
device = "cuda" if torch.cuda.is_available() else "cpu"

clip_model, _, preprocess = open_clip.create_model_and_transforms(
    'ViT-B-32',
    pretrained='openai'
)
clip_model = clip_model.to(device)
clip_model.eval()


def extract_feature(image_path):
    img = Image.open(image_path).convert("RGB")

    results = model(image_path)

    if results and len(results[0].boxes) > 0:
        # lấy box có confidence cao nhất
        boxes = results[0].boxes
        best_box = max(boxes, key=lambda b: float(b.conf[0]))

        x1, y1, x2, y2 = map(int, best_box.xyxy[0].cpu().numpy())
        img = img.crop((x1, y1, x2, y2))

    img_tensor = preprocess(img).unsqueeze(0).to(device)

    with torch.no_grad():
        feature = clip_model.encode_image(img_tensor)

    feature = feature.cpu().numpy().flatten()
    feature = feature / np.linalg.norm(feature)

    return feature