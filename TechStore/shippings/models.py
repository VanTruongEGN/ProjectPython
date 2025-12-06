import uuid

from django.db import models

# Create your models here.
class ShippingPartner(models.Model):
    id = models.CharField(primary_key=True, editable=False, verbose_name="Mã ĐVVC")
    name = models.CharField(max_length=255, verbose_name="Tên đơn vị vận chuyển")
    code = models.CharField(max_length=255, null=True, blank=True, verbose_name="Mã code")
    logo_url = models.CharField(max_length=500, null=True, blank=True, verbose_name="Logo")
    is_active = models.BooleanField(default=True, verbose_name="Hoạt động")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")

    class Meta:
        verbose_name = "Đơn vị vận chuyển"
        verbose_name_plural = "Danh sách đơn vị vận chuyển"

    def __str__(self):
        return self.name
class OrderShipping(models.Model):
    order = models.OneToOneField('orders.Order', primary_key=True, on_delete=models.CASCADE, verbose_name="Mã đơn hag")
    partner = models.ForeignKey(ShippingPartner, on_delete=models.CASCADE, verbose_name="Đơn vị vận chuyển")
    tracking_number = models.CharField(max_length=255, null=True, blank=True, verbose_name="Mã vận đơn")
    shipping_fee = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Phí vận chuyển")
    cod_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="COD thu hộ")
    weight_gram = models.IntegerField(null=True, blank=True, verbose_name="Khối lượng (gram)")
    status = models.CharField(max_length=20, default='đang xử lý', verbose_name="Trạng thái")
    shipped_at = models.DateTimeField(null=True, blank=True, verbose_name="Ngày gửi hàng")
    delivered_at = models.DateTimeField(null=True, blank=True, verbose_name="Ngày giao hàng")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")

    class Meta:
        verbose_name = "Thông tin vận chuyển"
        verbose_name_plural = "Danh sách vận chuyển"

    def __str__(self):
        return f"Vận chuyển {self.order_id}"