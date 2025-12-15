from accounts.models import Cart, CartItem
from products.models import Product

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
            item, created = CartItem.objects.get_or_create(
                cart=cart,
                product_id=product_id,
                defaults={"quantity": data["qty"]}
            )
            if not created:
                item.quantity += data["qty"]
                item.save()
        except Product.DoesNotExist:
            continue

    del request.session["cart"]
