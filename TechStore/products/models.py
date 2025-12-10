from django.db import models
from django.urls import reverse
from django.utils import timezone
class Category(models.Model):
    name = models.CharField("Tên danh mục", max_length=150)
    description = models.TextField("Mô tả", blank=True)
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='children',
        verbose_name="Danh mục cha"
    )
    created_at = models.DateTimeField("Ngày tạo", auto_now_add=True)

    class Meta:
        verbose_name = "Danh mục"
        verbose_name_plural = "Danh mục"
        ordering = ['name']

    def __str__(self):
        full_path = [self.name]
        parent = self.parent
        while parent is not None:
            full_path.append(parent.name)
            parent = parent.parent
        return ' → '.join(full_path[::-1])

    def get_absolute_url(self):
        return reverse('product:category', kwargs={'pk': self.pk})


class Product(models.Model):
    id = models.CharField("ID", primary_key=True, max_length=100,)
    name = models.CharField("Tên sản phẩm", max_length=300)
    description = models.TextField("Mô tả", blank=True)
    price = models.DecimalField("Giá", max_digits=12, decimal_places=0)

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name="Danh mục",
    )

    brand = models.CharField("Hãng", max_length=100, blank=True)
    model = models.CharField("Model", max_length=100, blank=True)
    
    image_main = models.ImageField(
        "Ảnh chính",
        upload_to='product/%Y/%m/%d/',
        blank=True,
        null=True
    )

    warranty_month = models.IntegerField("Bảo hành (tháng)", default=12)
    created_at = models.DateTimeField("Ngày tạo", auto_now_add=True, editable=False)
    updated_at = models.DateTimeField("Ngày cập nhật", auto_now=True, editable=False)
    status = models.BooleanField("Hiển thị", default=True)

    class Meta:
        verbose_name = "Sản phẩm"
        verbose_name_plural = "Danh sách sản phẩm"
        ordering = ['-created_at']
        db_table = 'Product'

    def __str__(self):
        return f"{self.id} - {self.name} - {self.price}"
    def save(self, *args, **kwargs):
        if not self.id:
            PREFIX = 'SP' 
            PADDING_LENGTH = 3

            last_product = Product.objects.filter(id__startswith=PREFIX).order_by('-id').first()

            if last_product:
                last_number_str = last_product.id.replace(PREFIX, '')
                try:
                    last_number = int(last_number_str)
                except ValueError:
                    last_number = 0
                new_number = last_number + 1
            else:
                new_number = 1
            self.id = f"{PREFIX}{str(new_number).zfill(PADDING_LENGTH)}"
        super().save(*args, **kwargs)
        
class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='images',
        verbose_name="Sản phẩm",
        null=True,
        blank=True
    )
    image = models.ImageField(
        "Ảnh sản phẩm", 
        upload_to='products/%Y/%m/%d/',
        blank=True,
        null=True
    )
    is_main = models.BooleanField("Đặt làm ảnh chính", default=False)
    uploaded_at = models.DateTimeField("Ngày đăng", auto_now_add=True)

    class Meta:
        verbose_name = "Ảnh sản phẩm"
        verbose_name_plural = "Ảnh sản phẩm"
        ordering = ['-is_main', 'uploaded_at']

    def __str__(self):
        return f"Ảnh của {self.product.name}"

    def save(self, *args, **kwargs):
        if self.is_main:
            ProductImage.objects.filter(product=self.product, is_main=True).update(is_main=False)
            
        super().save(*args, **kwargs)
        
        if self.is_main:
             Product.objects.filter(pk=self.product.pk).update(image_main=self.image)

class ProductAttribute(models.Model):
     product = models.ForeignKey(Product,verbose_name="Mã sản phẩm",on_delete=models.CASCADE)
     attribute = models.CharField("Tên thuộc tính", max_length=100)
     value = models.CharField("Thông tin thuộc tính",max_length=100)

     class Meta:
         unique_together = ('product', 'attribute')


class ProductDiscount(models.Model):
    id = models.CharField(primary_key=True,verbose_name="Mã chương trình")
    product = models.ForeignKey(Product,verbose_name="Mã sản phẩm",on_delete=models.SET_NULL,null=True)
    original_price = models.DecimalField(verbose_name="Giá gốc",max_digits=12, decimal_places=2, null=True, blank=True)
    discounted_price = models.DecimalField(verbose_name="Giá đã giảm",max_digits=12, decimal_places=2)
    start_date = models.DateTimeField(verbose_name="Ngày bắt đầu",null=True, blank=True)
    end_date = models.DateTimeField(verbose_name="Ngày kết thúc",null=True, blank=True)
    created_at = models.DateTimeField(verbose_name="Ngày thêm vào",auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.id:
            PREFIX = 'CT' 
            PADDING_LENGTH = 3

            last_record = ProductDiscount.objects.filter(id__startswith=PREFIX).order_by('-id').first()

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

        if self.product:
            self.original_price = self.product.price
        super().save(*args, **kwargs)

