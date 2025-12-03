from django.db import models
from django.urls import reverse

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
    created_at = models.DateTimeField("Ngày tạo", auto_now_add=True)
    updated_at = models.DateTimeField("Ngày cập nhật", auto_now=True)
    status = models.BooleanField("Hiển thị", default=True)

    class Meta:
        verbose_name = "Sản phẩm"
        verbose_name_plural = "Danh sách sản phẩm"
        ordering = ['-created_at']
        db_table = 'Product'

    def __str__(self):
        return self.name

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
     product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
     )
     attribute = models.CharField("Tên thuộc tính", max_length=100)
     value = models.CharField("Thông tin thuộc tính",max_length=100)