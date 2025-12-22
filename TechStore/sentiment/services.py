# sentiment/services.py
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

MODEL_PATH = "sentiment/model/phobert_sentiment"

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
model.to(device)
model.eval()

LABEL_MAP = {
    0: "tiêu cực",
    1: "trung lập",
    2: "tích cực"
}

def predict_sentiment(text):
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=256
    ).to(device)

    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.softmax(outputs.logits, dim=-1)
        label_id = torch.argmax(probs).item()

    return {
        "label": LABEL_MAP[label_id],
        "score": probs[0][label_id].item()
    }
