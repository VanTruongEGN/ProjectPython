from django.db import transaction
from django.db.models import F
from .models import StoreReservation, StoreInventory
from orders.models import Order
@transaction.atomic
def payment_success(order):
    reservations = StoreReservation.objects.select_for_update().filter(
        order=order,
        status="Pending"
    )

    for r in reservations:
        StoreInventory.objects.select_for_update().filter(
            store=r.store,
            product=r.product
        ).update(
            stock=F("stock") - r.quantity,
            reserved_stock=F("reserved_stock") - r.quantity
        )

        r.status = "Completed"
        r.save(update_fields=["status"])

    order.status = "Đã thanh toán"
    order.save(update_fields=["status"])
