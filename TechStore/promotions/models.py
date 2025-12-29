import uuid
from django.db import models
from django.utils import timezone

class PromotionEvent(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField("Tên sự kiện", max_length=255)
    start_date = models.DateTimeField("Bắt đầu")
    end_date = models.DateTimeField("Kết thúc")
    is_active = models.BooleanField("Đang hoạt động", default=True)
    description = models.TextField("Mô tả", blank=True)

    class Meta:
        verbose_name = "Sự kiện khuyến mãi"
        verbose_name_plural = "Sự kiện khuyến mãi"

    def __str__(self):
        return f"{self.name} ({self.start_date.strftime('%d/%m')} - {self.end_date.strftime('%d/%m')})"

    def is_currently_active(self):
         now = timezone.now()
         return self.is_active and self.start_date <= now <= self.end_date


class PromotionRule(models.Model):
    """
    Luật khuyến mãi (Promotion Rule).
    Mỗi luật thuộc về 1 Sự kiện.
    Định nghĩa: Giảm bao nhiêu, cho sản phẩm nào, điều kiện là gì.
    """
    DISCOUNT_TYPES = (
        ('PERCENTAGE', 'Giảm theo %'),
        ('FIXED', 'Giảm số tiền cố định'),
    )
    
    event = models.ForeignKey(PromotionEvent, on_delete=models.CASCADE, related_name='rules', verbose_name="Sự kiện")
    name = models.CharField("Tên quy tắc", max_length=255)
    discount_type = models.CharField("Loại giảm giá", max_length=20, choices=DISCOUNT_TYPES)
    discount_value = models.DecimalField("Giá trị giảm", max_digits=12, decimal_places=2) 
    min_quantity = models.IntegerField("Số lượng tối thiểu", default=1) 
    min_order_value = models.DecimalField("Giá trị đơn tối thiểu", default=0, max_digits=12, decimal_places=2)
    products = models.ManyToManyField('products.Product', blank=True, related_name='promotion_rules', verbose_name="Sản phẩm áp dụng")
    
    class Meta:
        verbose_name = "Quy tắc khuyến mãi"
        verbose_name_plural = "Quy tắc khuyến mãi"

    def __str__(self):
        return f"{self.name} ({self.get_discount_type_display()} {int(self.discount_value)})"

    def calculate_discount(self, product_price, quantity=1):
        """
        Tính toán số tiền được giảm trên 1 đơn vị sản phẩm (unit discount).
        """
        discount_amount = 0
        if self.discount_type == 'PERCENTAGE':
             discount_amount = product_price * (self.discount_value / 100)
        elif self.discount_type == 'FIXED':
             discount_amount = self.discount_value

        if discount_amount > product_price:
            discount_amount = product_price
            
        return discount_amount
