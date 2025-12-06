from django.contrib import admin
from .models import Promotion, PromotionProduct, PromotionUsageLog

# Register your models here.
class PromotionProductInline(admin.TabularInline):
    model = PromotionProduct
    extra = 1
    fields = ('product',)

class PromotionUsageLogInline(admin.TabularInline):
    model = PromotionUsageLog
    extra = 0
    readonly_fields = ('used_at',)
    fields = ('customer', 'order', 'used_at')

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'discount_type', 'discount_value', 'status')
    search_fields = ('code', 'name')
    list_filter = ('discount_type', 'status', 'start_date', 'end_date','name')
    inlines = [PromotionProductInline, PromotionUsageLogInline]