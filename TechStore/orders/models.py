
from django.db import models
# Create your models here.


class Payment(models.Model):
    id = models.CharField(verbose_name="ID",primary_key=True, editable=False)
    method = models.CharField(verbose_name="Phương thức tt",max_length=100)
    gateway_transaction_id = models.CharField(verbose_name="Cổng thanh toán",max_length=255, null=True, blank=True)
    amount = models.DecimalField(verbose_name="Tổng tiền",max_digits=12, decimal_places=2)
    status = models.CharField(verbose_name="Trạng thái",max_length=20, default='Đã thanh toán')
    paid_at = models.DateTimeField(verbose_name="Ngày thanh toán",null=True, blank=True)
    created_at = models.DateTimeField(verbose_name="Ngày thêm vào",auto_now_add=True)


class Order(models.Model):
    id = models.CharField(primary_key=True, editable=False, verbose_name="Mã đơn hàng")
    customer = models.ForeignKey('accounts.Customer', on_delete=models.CASCADE, verbose_name="Khách hàng")
    address = models.ForeignKey('accounts.Address' , null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Mã địa chỉ")
    payment = models.ForeignKey(Payment, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Mã PTTT")
    promotion = models.ForeignKey('promotions.Promotion', null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Mã khuyến mãi")
    order_date = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo đơn")
    status = models.CharField(max_length=20, default='đang chờ xử lý', verbose_name="Trạng thái đơn hàng")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Tổng tiền")
    shipping_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Phí vận chuyển")
    note = models.TextField(null=True, blank=True, verbose_name="Ghi chú")
    pickup_store_id = models.ForeignKey('stores.Store', null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Cửa hàng nhận hàng")

    class Meta:
        verbose_name = "Đơn hàng"
        verbose_name_plural = "Đơn hàng"

    def __str__(self):
        return f"Đơn hàng {self.id}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name="Đơn hàng")
    product_id = models.ForeignKey('products.Product', null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Sản phẩm")
    quantity = models.IntegerField(verbose_name="Số lượng")
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Đơn giá")
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Tiền giảm giá")

    class Meta:
        unique_together = ('order', 'product_id')
        verbose_name = "Chi tiết đơn hàng"
        verbose_name_plural = "Chi tiết đơn hàng"

    def __str__(self):
        return f"{self.product_id} - SL: {self.quantity}"


class Shipping(models.Model):
    order_id = models.OneToOneField(Order, primary_key=True, on_delete=models.CASCADE, verbose_name="Mã Đơn hàng")
    shipping_method = models.CharField(max_length=255, verbose_name="Phương thức vận chuyển")
    shipping_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Phí vận chuyển")
    tracking_number = models.CharField(max_length=255, null=True, blank=True, verbose_name="Mã vận đơn")
    shipped_date = models.DateTimeField(null=True, blank=True, verbose_name="Ngày gửi hàng")
    delivered_date = models.DateTimeField(null=True, blank=True, verbose_name="Ngày giao hàng")
    status = models.CharField(max_length=20, default='đang chờ xử lý', verbose_name="Trạng thái vận chuyển")

    class Meta:
        verbose_name = "Thông tin vận chuyển"
        verbose_name_plural = "Thông tin vận chuyển"

    def __str__(self):
        return f"Vận chuyển của đơn {self.order_id_id}"