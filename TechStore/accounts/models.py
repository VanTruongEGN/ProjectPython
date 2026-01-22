import uuid

from django.db import models
from django.contrib.auth.models import User

class Customer(models.Model):
    id = models.CharField(primary_key=True, verbose_name="ID")
    email = models.EmailField(verbose_name="Email", unique=True)
    password_hash = models.CharField(verbose_name="Passwork_hash", max_length=255)
    full_name = models.CharField(verbose_name="Họ và tên", max_length=255, null=True, blank=True)
    phone = models.CharField(verbose_name="Số điện thoại", max_length=20, null=True, blank=True)
    date_of_birth = models.DateField(verbose_name="Ngày sinh", null=True, blank=True)
    gender = models.CharField(verbose_name="Giới tính", max_length=10, null=True, blank=True)
    status = models.CharField(verbose_name="Trạng thái", default="Hoạt động")
    created_at = models.DateTimeField(verbose_name="Ngày tạo", auto_now_add=True, null=True)
    otp = models.CharField(max_length=6, null=True, blank=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)




    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        if not self.id:
            PREFIX = 'KH'
            PADDING_LENGTH = 3

            last_record = Customer.objects.filter(id__startswith=PREFIX).order_by('-id').first()

            if last_record:
                last_number_str = last_record.id.replace(PREFIX, '')
                try:
                    last_number = int(last_number_str)
                except ValueError:
                    last_number = 0
                new_number = last_number + 1
            else:
                new_number = 1
            self.id = f"{PREFIX}{str(new_number).zfill(PADDING_LENGTH)}"
        super().save(*args, **kwargs)
    class Meta:
        verbose_name = "Khách hàng"
        verbose_name_plural = "Khách hàng"

class Address(models.Model):
    id = models.CharField(verbose_name="ID",primary_key=True)
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

    def save(self, *args, **kwargs):
        if not self.id:
            PREFIX = 'DC'
            PADDING_LENGTH = 3
            last_record = Address.objects.filter(id__startswith=PREFIX).order_by('-id').first()
            if last_record:
                last_number_str = last_record.id.replace(PREFIX, '')
                try:
                    last_number = int(last_number_str)
                except ValueError:
                    last_number = 0
                new_number = last_number + 1
            else:
                new_number = 1
            self.id = f"{PREFIX}{str(new_number).zfill(PADDING_LENGTH)}"

        # Nếu địa chỉ này được chọn là mặc định, thì bỏ mặc định ở các địa chỉ khác
        if self.is_default:
            Address.objects.filter(customer=self.customer, is_default=True).exclude(id=self.id).update(is_default=False)

        super().save(*args, **kwargs)


class Wishlist(models.Model):
    customer = models.ForeignKey(Customer, verbose_name="Mã khách hàng",on_delete=models.CASCADE)
    product = models.ForeignKey('products.Product', verbose_name="Mã sản phẩm",on_delete=models.CASCADE)
    added_at = models.DateTimeField(verbose_name="Ngày thêm vào",auto_now_add=True)

    class Meta:
        unique_together = ('customer', 'product')


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Giỏ hàng"
        verbose_name_plural = "Giỏ hàng"

    def __str__(self):
        return f"Cart of {self.customer.email}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, verbose_name="Mã giỏ hàng",on_delete=models.CASCADE)
    product = models.ForeignKey('products.Product', verbose_name="Mã sản phẩm",on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name="Số lượng",default=1)
    price_at_add = models.DecimalField(verbose_name="Gía",max_digits=12, decimal_places=2)
    added_at = models.DateTimeField(verbose_name="Ngày thêm vào",auto_now_add=True)

    class Meta:
        unique_together = ('cart', 'product')



