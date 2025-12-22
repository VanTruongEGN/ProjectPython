from django.contrib import admin
from .models import Comment

# Register your models here.
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('customer', 'product', 'rating','label', 'is_approved', 'created_at')
    search_fields = ('customer__id','product__name','product__id')
    list_filter = ('rating', 'product')

    def customer_email(self, obj):
        return obj.customer.email
    customer_email.short_description = 'Customer Email'

    def product_name(self, obj):
        return obj.product.name
    product_name.short_description = 'Product Name'