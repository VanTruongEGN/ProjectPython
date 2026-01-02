import hmac
import hashlib
import urllib.parse
from datetime import datetime

class VNPay:
    def __init__(self, tmn_code, hash_secret, payment_url, return_url):
        self.tmn_code = tmn_code.strip()
        self.hash_secret = hash_secret.strip()
        self.payment_url = payment_url.strip()
        self.return_url = return_url.strip()

    def create_payment_url(self, request, order_id, amount, order_desc, order_type="250000"):
        create_date = datetime.now().strftime("%Y%m%d%H%M%S")

        vnp_params = {
            "vnp_Version": "2.1.0",
            "vnp_Command": "pay",
            "vnp_TmnCode": self.tmn_code,
            "vnp_Amount": str(int(round(amount * 100))),
            "vnp_CurrCode": "VND",
            "vnp_TxnRef": str(order_id),
            "vnp_OrderInfo": order_desc,
            "vnp_OrderType": order_type,
            "vnp_Locale": "vn",
            "vnp_ReturnUrl": self.return_url,
            "vnp_IpAddr": "127.0.0.1",
            "vnp_CreateDate": create_date,
        }

        sorted_items = sorted(vnp_params.items())
        sign_data = "&".join(f"{k}={v}" for k, v in sorted_items)

        secure_hash = hmac.new(
            self.hash_secret.encode("utf-8"),
            sign_data.encode("utf-8"),
            hashlib.sha512
        ).hexdigest().lower()

        query_string = urllib.parse.urlencode(vnp_params)
        payment_url = f"{self.payment_url}?{query_string}&vnp_SecureHash={secure_hash}"

        return payment_url


# === TEST NGAY TẠI ĐÂY ===
vnp = VNPay(
    tmn_code="J4X8OO7F",  # MỚI
    hash_secret="GET0FWM9GA9V8W0PSDIE09S5M7S3MJAN",  # MỚI
    payment_url="https://sandbox.vnpayment.vn/paymentv2/vpcpay.html",
    return_url="http://127.0.0.1:8000/accounts/vnpay_return/"
)

class FakeRequest:
    pass

request = FakeRequest()

url = vnp.create_payment_url(
    request=request,
    order_id="TEST123",
    amount=50000,  # 500 VND
    order_desc="Test thanh toan VNPAY"
)

print("URL thanh toán:")
print(url)