from orders.models import OrderItem, Order

def has_purchased_product(customer, product):
    return OrderItem.objects.filter(
        order__customer=customer,
        order__status__in=["Đã thanh toán"],
        product=product
    ).exists()