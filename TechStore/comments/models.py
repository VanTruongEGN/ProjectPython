import uuid

from django.db import models

# Create your models here.
class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, verbose_name="ID")
    customer = models.ForeignKey('accounts.Customer', on_delete=models.SET_NULL, null=True, verbose_name="Mã khách hàng")
    product = models.ForeignKey('products.Product', on_delete=models.SET_NULL , null=True, verbose_name="Mã sản phẩm")
    rating = models.IntegerField(verbose_name="Số sao")
    content = models.TextField(null=True, blank=True, verbose_name="Nội dung")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    label = models.CharField(max_length=20, null=True, blank=True, verbose_name="Cảm xúc")
    is_approved = models.BooleanField(default=True, verbose_name="Đã duyệt")
    is_spam = models.BooleanField(default=False)
    spam_score = models.FloatField(default=0, verbose_name="Điểm spam")
    class Meta:
        verbose_name = "Bình luận"
        verbose_name_plural = "Danh sách bình luận"

    def __str__(self):
        return f"{self.customer} - {self.product} ({self.rating})"