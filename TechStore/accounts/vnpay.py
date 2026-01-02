import hmac
import hashlib
import urllib.parse
from datetime import datetime

class VNPay:
    def __init__(self, tmn_code, hash_secret, payment_url, return_url):
        self.tmn_code = tmn_code
        self.hash_secret = hash_secret
        self.payment_url = payment_url
        self.return_url = return_url

    def create_payment_url(self, request, order_id, amount, order_desc):
        vnp_params = {
            "vnp_Version": "2.1.0",
            "vnp_Command": "pay",
            "vnp_TmnCode": self.tmn_code,
            "vnp_Amount": int(amount * 100),  # BẮT BUỘC *100
            "vnp_CurrCode": "VND",
            "vnp_TxnRef": str(order_id),
            "vnp_OrderInfo": order_desc,
            "vnp_OrderType": "other",
            "vnp_Locale": "vn",
            "vnp_ReturnUrl": self.return_url,
            "vnp_IpAddr": self.get_client_ip(request),
            "vnp_CreateDate": datetime.now().strftime("%Y%m%d%H%M%S"),
        }

        # sort params
        sorted_params = sorted(vnp_params.items())
        query_string = urllib.parse.urlencode(sorted_params)

        # hash
        hash_data = query_string.encode("utf-8")
        secure_hash = hmac.new(
            self.hash_secret.encode("utf-8"),
            hash_data,
            hashlib.sha512
        ).hexdigest()

        return f"{self.payment_url}?{query_string}&vnp_SecureHash={secure_hash}"

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0]
        return request.META.get("REMOTE_ADDR", "127.0.0.1")
