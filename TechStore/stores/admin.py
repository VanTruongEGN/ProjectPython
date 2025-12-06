from django.contrib import admin
from .models import Store, StoreInventory, StoreReservation

# Register your models here.

class StoreInventoryInline(admin.TabularInline):
    model = StoreInventory
    extra = 1
    fields = ('product', 'stock', 'reserved_stock')

class StoreReservationInline(admin.TabularInline):
    model = StoreReservation
    extra = 1
    fields = ('customer', 'product', 'quantity', 'status', 'reserved_at', 'expired_at')

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'district', 'phone')
    search_fields = ('name', 'city', 'district')
    list_filter = ('city', 'district')
    inlines = [StoreInventoryInline, StoreReservationInline]