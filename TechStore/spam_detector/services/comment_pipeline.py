from spam_detector.rules import rule_filter
from spam_detector.services.spam_predictor import predict_spam_prob
from sentiment.services import predict_sentiment

SPAM_THRESHOLD = 0.7


def process_comment(text: str) -> dict:
    # Tầng 1: rule
    if rule_filter(text):
        print(f"DEBUG: Comment filtered by rule: {text}")
        return {
            "is_spam": True,
            "spam_source": "rule"
        }

    # Tầng 2: PhoBERT spam
    if len(text.strip()) <= 5:
        is_spam = False
        spam_score = 0.0
    else:
        spam_score = predict_spam_prob(text)
        is_spam = spam_score >= 0.7

    print(f"DEBUG: Spam prob for '{text}': {spam_score}")
    if is_spam:
        return {
            "is_spam": True,
            "spam_source": "model",
            "spam_prob": spam_score
        }

    # Tầng 3: sentiment
    sentiment = predict_sentiment(text)
    print(f"DEBUG: Sentiment for '{text}': {sentiment}")
    return {
        "is_spam": False,
        "sentiment": sentiment
    }