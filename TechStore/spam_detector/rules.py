import re

PHONE_REGEX = re.compile(r"(0|\+84)\d{8,10}")

def rule_filter(text: str) -> bool:
    text = text.lower()
    if len(text) <= 10:
        return False
    if text.count("http") >= 2:
        return True

    if PHONE_REGEX.search(text):
        return True

    if text.count("zalo") >= 1 or text.count("ib") >= 2:
        return True

    return False
