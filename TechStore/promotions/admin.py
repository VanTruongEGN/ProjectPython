from django.contrib import admin
from .models import PromotionEvent, PromotionRule

class PromotionRuleInline(admin.TabularInline):
    model = PromotionRule
    extra = 1
    filter_horizontal = ('products',) 

@admin.register(PromotionEvent)
class PromotionEventAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active', 'start_date', 'end_date')
    search_fields = ('name',)
    inlines = [PromotionRuleInline]

@admin.register(PromotionRule)
class PromotionRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'event', 'discount_type', 'discount_value', 'min_quantity')
    list_filter = ('discount_type', 'event')
    search_fields = ('name', 'event__name')
    filter_horizontal = ('products',)