import torch
from .model_loader import tokenizer, model, device

def predict_spam_prob(text: str) -> float:
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=256
    ).to(device)

    with torch.no_grad():
        logits = model(**inputs).logits
        prob_spam = torch.softmax(logits, dim=-1)[0][1].item()

    return prob_spam
