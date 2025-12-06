import uuid

from django.db import models

# Create your models here.

class Promotion(models.Model):
    id = models.CharField(primary_key=True, editable=False, verbose_name="ID")
    code = models.CharField(max_length=255, unique=True, verbose_name="Mã code")
    name = models.CharField(max_length=255, verbose_name="Tên khuyến mãi")
    description = models.TextField(null=True, blank=True, verbose_name="Mô tả")
    discount_type = models.CharField(max_length=20, verbose_name="Loại giảm giá")  # percent | fixed
    discount_value = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Giá trị giảm")
    min_order_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Giá trị đơn hàng tối thiểu")
    max_discount_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Giảm tối đa")
    start_date = models.DateField(null=True, blank=True, verbose_name="Ngày bắt đầu")
    end_date = models.DateField(null=True, blank=True, verbose_name="Ngày kết thúc")
    usage_limit = models.IntegerField(null=True, blank=True, verbose_name="Giới hạn số lượt dùng")
    used_count = models.IntegerField(default=0, verbose_name="Số lượt đã dùng")
    status = models.CharField(max_length=20, default='active', verbose_name="Trạng thái")

    class Meta:
        verbose_name = "Khuyến mãi"
        verbose_name_plural = "Khuyến mãi"

    def __str__(self):
        return f"{self.name} ({self.code})"


class PromotionProduct(models.Model):
    promotion = models.ForeignKey(Promotion, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Mã khuyến mãi")
    product_id = models.ForeignKey('products.Product', null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Mã sản phẩm")

    class Meta:
        unique_together = ('promotion', 'product_id')
        verbose_name = "Sản phẩm áp dụng khuyến mãi"
        verbose_name_plural = "Sản phẩm áp dụng khuyến mãi"

    def __str__(self):
        return f"{self.product_id} — {self.promotion}"


class PromotionUsageLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name="ID")
    promotion = models.ForeignKey(Promotion, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Khuyến mãi")
    customer = models.ForeignKey('accounts.Customer', null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Khách hàng")
    order = models.ForeignKey('orders.Order', null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Đơn hàng")
    used_at = models.DateTimeField(auto_now_add=True, verbose_name="Thời gian sử dụng")

    class Meta:
        verbose_name = "Lịch sử sử dụng khuyến mãi"
        verbose_name_plural = "Lịch sử sử dụng khuyến mãi"

    def __str__(self):
        return f"Log {self.id} — {self.promotion}"