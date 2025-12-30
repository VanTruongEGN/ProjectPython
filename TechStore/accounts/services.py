from accounts.models import Cart, CartItem
from products.models import Product
from django.utils import timezone
from decimal import Decimal

def get_or_create_user_cart(customer):
    cart, _ = Cart.objects.get_or_create(customer=customer)
    return cart


def merge_session_cart_to_db(request, customer):
    session_cart = request.session.get("cart")
    if not session_cart:
        return

    cart = get_or_create_user_cart(customer)

    for product_id, data in session_cart.items():
        try:
            product = Product.objects.get(id=product_id)



            
            price_at_add = (
                Decimal(data["price"])
                if "price" in data
                else product.price
            )

            item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={
                    "quantity": data["qty"],
                    "price_at_add": price_at_add
                }
            )

            if not created:
                item.quantity += data["qty"]
                item.save()

        except Product.DoesNotExist:
            continue

    del request.session["cart"]
