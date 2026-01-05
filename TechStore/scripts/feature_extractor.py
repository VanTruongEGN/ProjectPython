import torch
import torchvision.models as models
import torchvision.transforms as T
from PIL import Image
import numpy as np

device = "cuda" if torch.cuda.is_available() else "cpu"

model = models.resnet18(pretrained=True)
model.fc = torch.nn.Identity()
model.eval().to(device)

transform = T.Compose([
    T.Resize((224, 224)),
    T.ToTensor(),
    T.Normalize(mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225])
])

def extract_feature(img_bgr):
    img_rgb = img_bgr[:, :, ::-1]
    img = Image.fromarray(img_rgb)

    x = transform(img).unsqueeze(0).to(device)
    with torch.no_grad():
        feat = model(x)

    return feat.cpu().numpy().flatten()