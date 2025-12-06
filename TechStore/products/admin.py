from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, ProductImage, ProductAttribute



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'created_at']
    search_fields = ['name']
    list_filter = ['created_at']

    def parent(self, obj):
        return obj.parent.name if obj.parent else "-"
    parent.short_description = "Danh mục cha"

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 2
    fields = ['image', 'is_main']

class ProductInfoInline(admin.TabularInline):
    model = ProductAttribute
    extra = 1
    fields = ['attribute','value']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'formatted_price', 'category', 'status', 'created_at']
    list_filter = ['status', 'category', 'brand', 'created_at']
    search_fields = ['name', 'brand', 'model']
    inlines = [ProductImageInline,ProductInfoInline]
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ("Thông tin cơ bản", {
            'fields': ('name', 'brand', 'model', 'category', 'status')
        }),
        ("Giá & Bảo hành", {
            'fields': ('price', 'warranty_month')
        }),
        ("Mô tả", {
            'fields': ('description',)
        }),
        ("Ảnh chính", {
            'fields': ('image_main',)
        }),
        ("Thời gian", {
            'fields': ('created_at', 'updated_at')
        }),
    )


    def formatted_price(self, obj):
        return f"{int(obj.price):,} ₫".replace(",", ".")
    formatted_price.short_description = "Giá bán"

