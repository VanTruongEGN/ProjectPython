import re

PHONE_REGEX = re.compile(r"(0|\+84)\d{8,10}")

def rule_filter(text: str) -> bool:
    spam_keywords = {"mua ngay", "giảm giá", "khuyến mãi",
            "liên hệ", "inbox", "ib",
            "trúng thưởng", "kiếm tiền online",
            "xxx", "18+", "vay"}
    text = text.lower()
    if any(kw in text for kw in spam_keywords):
        return True
    if len(text) <= 10:
        return False
    if text.count("http") >= 2:
        return True

    if PHONE_REGEX.search(text):
        return True

    if text.count("zalo") >= 1 or text.count("ib") >= 2:
        return True

    return False