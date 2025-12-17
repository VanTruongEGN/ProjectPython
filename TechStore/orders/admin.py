from django.contrib import admin
from .models import Order, OrderItem, Shipping, Payment
from stores.service import payment_success
# Register your models here.

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    fields = ('product', 'quantity', 'unit_price', 'discount_amount')

class ShippingInline(admin.TabularInline):
    model = Shipping
    extra = 1
    fields = ('shipping_method', 'shipping_cost', 'tracking_number', 'status')

@admin.action(description="Xác nhận đã thanh toán")
def confirm_payment(modeladmin, request, queryset):
    for order in queryset:
        if order.status != "Đã thanh toán":
            payment_success(order)
            order.status = "Đã thanh toán"
            order.save(update_fields=["status"])
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    readonly_fields = ['id']
    list_display = ('id', 'customer_email', 'status', 'total_amount', 'order_date')
    search_fields = ('id', 'customer__email')
    list_filter = ('status', 'order_date','id')
    inlines = [OrderItemInline, ShippingInline]
    actions = [confirm_payment]

    def customer_email(self, obj):
        return obj.customer.email
    customer_email.short_description = 'Customer Email'

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    readonly_fields = ['id']
    list_display = ('method', 'amount', 'status', 'paid_at')
    search_fields = ('method', 'gateway_transaction_id')
    list_filter = ('status','method')