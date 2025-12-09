from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, ProductImage, ProductAttribute, ProductDiscount


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

class ProductAttributeInline(admin.TabularInline):
    model = ProductAttribute
    fk_name = "product"
    extra = 1
    fields = ['attribute', 'value']

    def product_name(self, obj):
        return obj.product.name
    product_name.short_description = 'Product Name'

    def category_name(self, obj):
        return obj.category.name if obj.category else None
    category_name.short_description = 'Category'

@admin.register(ProductDiscount)
class ProductDiscountAdmin(admin.ModelAdmin):
    readonly_fields = ['id']
    list_display = ('id', 'product_name', 'original_price', 'discounted_price', 'start_date', 'end_date', 'created_at')
    list_filter = ('start_date', 'end_date')

    def product_name(self, obj):
        return obj.product.name
    product_name.short_description = 'Product Name'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id','name', 'brand', 'formatted_price', 'category', 'status', 'created_at']
    list_filter = ['status', 'category', 'brand', 'created_at']
    search_fields = ['name', 'brand', 'model']
    inlines = [ProductImageInline, ProductAttributeInline]
    readonly_fields = ['id','created_at','updated_at']
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

    )


    def formatted_price(self, obj):
        return f"{int(obj.price):,} ₫".replace(",", ".")
    formatted_price.short_description = "Giá bán"

