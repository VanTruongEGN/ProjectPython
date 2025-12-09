from django.db import models

# Create your models here.
import uuid
from django.db import models
from accounts.models import Customer
from products.models import Product


class Store(models.Model):
    id = models.CharField(primary_key=True, editable=False, verbose_name="ID")
    name = models.CharField(max_length=255, verbose_name="Tên cửa hàng")
    phone = models.CharField(max_length=20, null=True, blank=True, verbose_name="Số điện thoại")
    address_line = models.CharField(max_length=255, verbose_name="Địa chỉ")
    ward = models.CharField(max_length=255, null=True, blank=True, verbose_name="Phường/Xã")
    district = models.CharField(max_length=255, verbose_name="Quận/Huyện")
    city = models.CharField(max_length=255, verbose_name="Tỉnh/Thành phố")

    class Meta:
        verbose_name = "Cửa hàng"
        verbose_name_plural = "Danh sách cửa hàng"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.id:
            PREFIX = 'CH' 
            PADDING_LENGTH = 3

            last_record = Store.objects.filter(id__startswith=PREFIX).order_by('-id').first()

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

class StoreInventory(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, verbose_name="Mã cửa hàng")
    product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Mã sản phẩm")
    stock = models.IntegerField(default=0, verbose_name="Tồn kho")
    reserved_stock = models.IntegerField(default=0, verbose_name="Đã giữ (reserved)") #khách hàng thêm vào nhưng chưa thanh toán

    class Meta:
        unique_together = ('store', 'product')
        verbose_name = "Kho"
        verbose_name_plural = "Danh sách tồn kho cửa hàng"

    def __str__(self):
        return f"{self.store} - {self.product}"


class StoreReservation(models.Model):
    id = models.CharField(primary_key=True, verbose_name="ID đặt hàng")
    store = models.ForeignKey(Store, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Cửa hàng")
    customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Khách hàng")
    product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Sản phẩm")
    quantity = models.IntegerField(verbose_name="Số lượng")
    status = models.CharField(max_length=20, verbose_name="Trạng thái")
    reserved_at = models.DateTimeField(auto_now_add=True, verbose_name="Thời điểm đặt hàng")
    expired_at = models.DateTimeField(null=True, blank=True, verbose_name="Thời điểm hết hạn")

    class Meta:
        verbose_name = "Cửa hàng nhận hàng"
        verbose_name_plural = "Danh sách của hàng nhận"

    def __str__(self):
        return f"Giữ hàng {self.product} tại {self.store}"

    def save(self, *args, **kwargs):
        if not self.id:
            PREFIX = 'PD' 
            PADDING_LENGTH = 3

            last_record = StoreReservation.objects.filter(id__startswith=PREFIX).order_by('-id').first()

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