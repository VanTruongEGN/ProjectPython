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
    fields = ('customer', 'product', 'quantity', 'status', 'expired_at')
    readonly_fields = ('reserved_at',) 
@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    readonly_fields = ['id']
    list_display = ('id','name', 'city', 'district', 'phone')
    search_fields = ('name', 'city', 'district')
    list_filter = ('city', 'district')
    inlines = [StoreInventoryInline, StoreReservationInline]