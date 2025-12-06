from django.contrib import admin
from .models import Customer, Address, Wishlist, Cart, CartItem
from orders.models import Order  # import Order từ app orders

# Register your models here.
# model bảng được inline
# extra form hiển thị
# fields những field được hiển thị trong inline
# readonly_fields những field chỉ đọc không thể sửa trong inline
class AddressInline(admin.TabularInline):
    model = Address
    extra = 1
    fields = ('recipient_name', 'phone', 'address_line', 'district', 'city', 'is_default')

class WishlistInline(admin.TabularInline):
    model = Wishlist
    extra = 1
    fields = ('product','added_at')


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1
    fields = ('product', 'quantity', 'price_at_add')

class OrderInline(admin.TabularInline):
    model = Order
    extra = 0
    fields = ('id', 'status', 'total_amount', 'order_date')
    readonly_fields = ('id', 'total_amount', 'order_date')

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'phone', 'status')
    search_fields = ('email', 'full_name', 'phone')
    list_filter = ('status',)
    inlines = [AddressInline, WishlistInline, OrderInline]

