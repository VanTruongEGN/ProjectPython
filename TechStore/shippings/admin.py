from django.contrib import admin
from .models import ShippingPartner, OrderShipping
# Register your models here.


@admin.register(ShippingPartner)
class ShippingPartnerAdmin(admin.ModelAdmin):
    readonly_fields = ['id']
    list_display = ('id','name', 'code', 'is_active')
    search_fields = ('name', 'code')
    list_filter = ('is_active','name','code')


@admin.register(OrderShipping)
class OrderShippingAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'partner_name', 'tracking_number', 'status')
    search_fields = ('order__id', 'tracking_number', 'partner__name')
    list_filter = ('status',)

    def partner_name(self, obj):
        return obj.partner.name
    partner_name.short_description = 'Shipping Partner'