import uuid

from django.db import models

# Create your models here.
class Customer(models.Model):
    id = models.CharField(primary_key=True, verbose_name="ID",editable=False)
    email = models.EmailField(verbose_name="Email",unique=True)
    password_hash = models.CharField(verbose_name="Passwork_hash",max_length=255)
    full_name = models.CharField(verbose_name="Họ và tên",max_length=255, null=True, blank=True)
    phone = models.CharField(verbose_name="Số điện thoại",max_length=20, null=True, blank=True)
    date_of_birth = models.DateField(verbose_name="Ngày sinh",null=True, blank=True)
    gender = models.CharField(verbose_name="Giới tính",max_length=10, null=True, blank=True)
    status = models.CharField(verbose_name="Trạng thái",default="Hoạt động")
    created_at = models.DateTimeField(verbose_name="Ngày tạo",auto_now_add=True)

    def __str__(self):
        return self.email


class Address(models.Model):
    id = models.CharField(verbose_name="ID",primary_key=True, editable=False)
    customer = models.ForeignKey(Customer, verbose_name="Mã khách hàng",on_delete=models.CASCADE, editable=False)
    recipient_name = models.CharField(verbose_name="Tên người nhận",max_length=255)
    phone = models.CharField(verbose_name="Số điện thoại",max_length=20)
    address_line = models.TextField(verbose_name="Đường")
    ward = models.CharField(verbose_name="Xã",max_length=255, null=True, blank=True)
    district = models.CharField(verbose_name="Quận/Huyện",max_length=255)
    city = models.CharField(verbose_name="Thành Phố",max_length=255)
    postal_code = models.CharField(max_length=20, null=True, blank=True)
    is_default = models.BooleanField(verbose_name="Địa chỉ mặc định",default=False)

    def __str__(self):
        return f"{self.recipient_name} - {self.address_line}"


class Wishlist(models.Model):
    customer = models.ForeignKey(Customer, verbose_name="Mã khách hàng",on_delete=models.CASCADE)
    product = models.ForeignKey('products.Product', verbose_name="Mã sản phẩm",on_delete=models.CASCADE)
    added_at = models.DateTimeField(verbose_name="Ngày thêm vào",auto_now_add=True)

    class Meta:
        unique_together = ('customer', 'product_id')


class Cart(models.Model):
    id = models.CharField(primary_key=True, editable=False, verbose_name="ID")
    customer = models.OneToOneField(Customer, verbose_name="Mã khách hàng", on_delete=models.CASCADE)
    class Meta:
        unique_together = ('customer', 'id')
    def __str__(self):
        return f"Cart of {self.customer.email}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, verbose_name="Mã giỏ hàng",on_delete=models.CASCADE)
    product = models.ForeignKey('products.Product', verbose_name="Mã sản phẩm",on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name="Số lượng",default=1)
    price_at_add = models.DecimalField(verbose_name="Gía",max_digits=12, decimal_places=2)
    added_at = models.DateTimeField(verbose_name="Ngày thêm vào",auto_now_add=True)

    class Meta:
        unique_together = ('cart', 'product_id')