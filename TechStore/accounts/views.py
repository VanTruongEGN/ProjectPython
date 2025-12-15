from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.hashers import make_password
from django.db import IntegrityError, transaction
from .models import Customer, CartItem, Address
from django.contrib.auth.hashers import check_password
from accounts.services import merge_session_cart_to_db, get_or_create_user_cart
from .models import Customer, CartItem, Address
from django.contrib.auth.hashers import check_password
from accounts.services import merge_session_cart_to_db, get_or_create_user_cart
from products.models import Product, ProductDiscount
from orders.models import Order, OrderItem, Payment
from django.utils import timezone
from decimal import Decimal

def signup_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        full_name = request.POST.get("full_name")

        # Kiểm tra email đã tồn tại chưa
        if Customer.objects.filter(email=email).exists():
            return render(request, "accounts/signup.html", {
                "error": "Email đã được sử dụng. Vui lòng chọn email khác."
            })

        # Mã hóa mật khẩu
        password_hash = make_password(password)

        try:
            # Tạo Customer mới
            customer = Customer(
                email=email,
                password_hash=password_hash,
                full_name=full_name
            )
            customer.save()
            return redirect("login")
        except IntegrityError:
            return render(request, "accounts/signup.html", {
                "error": "Đăng ký thất bại do lỗi hệ thống. Vui lòng thử lại."
            })

    return render(request, "accounts/signup.html")


def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            customer = Customer.objects.get(email=email)
            if check_password(password, customer.password_hash):
                # Đăng nhập thành công → lưu session
                request.session["customer_id"] = str(customer.id)
                request.session["customer_email"] = customer.email
                merge_session_cart_to_db(request, customer)
                return redirect("home") 
            else:
                error = "Sai mật khẩu. Vui lòng thử lại."
        except Customer.DoesNotExist:
            error = "Email không tồn tại."

        return render(request, "accounts/login.html", {"error": error})
    return render(request, "accounts/login.html")

@transaction.atomic
def process_checkout(request):
    if request.method != "POST":
        return redirect("cart")

    if not request.session.get("customer_id"):
        return redirect("login")
    customer = Customer.objects.get(id=request.session["customer_id"])
    cart = get_or_create_user_cart(customer)

    cart_items = CartItem.objects.filter(cart=cart).select_related("product")
    if not cart_items.exists():
        return redirect("cart")

    total = 0
    for item in cart_items:
        total += item.quantity * item.price_at_add

    address = Address.objects.filter(customer=customer, is_default=True).first() \
              or Address.objects.filter(customer=customer).first()

    payment = Payment.objects.create(
        method=request.POST.get("payment_method", "COD"),
        amount=total,
        status="Chưa thanh toán"
    )

    order = Order.objects.create(
        customer=customer,
        address=address,
        payment=payment,
        total_amount=total,
        status="Đang xử lý",
        note=request.POST.get("note", "")
    )

    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            unit_price=item.price_at_add
        )

    cart_items.delete()
    return redirect("home")



def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    qty = int(request.POST.get("quantity", 1))

    discount = ProductDiscount.objects.filter(
        product=product,
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now()
    ).first()
    price_at_add = discount.discounted_price if discount else product.price

    if request.session.get("customer_id"):
        customer = Customer.objects.get(id=request.session["customer_id"])
        cart = get_or_create_user_cart(customer)

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={
                "quantity": qty,
                "price_at_add": price_at_add
            }
        )
        if not created:
            item.quantity += qty
            item.save()

    else:
        cart = request.session.get("cart", {})
        if str(product.id) in cart:
            cart[str(product.id)]["qty"] += qty
        else:
            cart[str(product.id)] = {
                "qty": qty,
                "price": str(price_at_add)
            }
        request.session["cart"] = cart

    return redirect(request.META.get("HTTP_REFERER", "/"))


def cart_view(request):
    items = []
    total = 0

    if request.session.get("customer_id"):
        customer = Customer.objects.get(id=request.session["customer_id"])
        cart = get_or_create_user_cart(customer)
        cart_items = CartItem.objects.filter(cart=cart).select_related("product")

        for item in cart_items:
            line_total = item.quantity * item.price_at_add
            total += line_total

            items.append({
                "id": item.id,
                "product": item.product,
                "quantity": item.quantity,
                "price": item.price_at_add,
                "line_total": line_total,
            })
    else:
        session_cart = request.session.get("cart", {})
        for product_id, data in session_cart.items():
            product = Product.objects.get(id=product_id)

            price = data.get("price", product.price)
            line_total = data["qty"] * Decimal(price)
            total += line_total

            items.append({
                "id": product.id,
                "product": product,
                "quantity": data["qty"],
                "price": price,
            "line_total": line_total,
        })


    user_address = None
    if request.session.get("customer_id"):
        user_address = Address.objects.filter(
            customer_id=request.session["customer_id"],
            is_default=True
        ).first() or Address.objects.filter(
            customer_id=request.session["customer_id"]
        ).first()

    return render(request, "accounts/cart.html", {
        "items": items,
        "total": total,
        "user_address": user_address
    })

def buy_now(request, product_id):
    if request.method != "POST":
        return redirect("productDetail", pk=product_id)

    product = get_object_or_404(Product, id=product_id)
    qty = int(request.POST.get("quantity", 1))
    
    discount = ProductDiscount.objects.filter(
        product=product,
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now()
    ).first()

    price_at_add = discount.discounted_price if discount else product.price
    if request.session.get("customer_id"):
        customer = Customer.objects.get(id=request.session["customer_id"])
        cart = get_or_create_user_cart(customer)

        CartItem.objects.filter(cart=cart).delete()

        CartItem.objects.create(
            cart=cart,
            product=product,
            quantity=qty,
            price_at_add=price_at_add
        )


    else:
        request.session["cart"] = {
            str(product.id): {"qty": qty}
        }

    return redirect("cart")

    
def cart_remove(request, item_id):

    if request.session.get("customer_id"):
        customer = Customer.objects.get(id=request.session["customer_id"])
        cart = get_or_create_user_cart(customer)
        CartItem.objects.filter(cart=cart, id=item_id).delete()

    else:
        cart = request.session.get("cart", {})
        cart.pop(str(item_id), None)
        request.session["cart"] = cart

    return redirect("cart")

def update_cart_quantity(request, item_id, action):
    if request.session.get("customer_id"):
        customer = Customer.objects.get(id=request.session["customer_id"])
        cart = get_or_create_user_cart(customer)
        item = get_object_or_404(CartItem, cart=cart, id=item_id)
        
        if action == "increase":
            item.quantity += 1
            item.save()
        elif action == "decrease":
            item.quantity -= 1
            if item.quantity <= 0:
                item.delete()
            else:
                item.save()
    else:
        cart = request.session.get("cart", {})

        if str(item_id) in cart:
            if action == "increase":
                cart[str(item_id)]["qty"] += 1
            elif action == "decrease":
                cart[str(item_id)]["qty"] -= 1
                if cart[str(item_id)]["qty"] <= 0:
                    cart.pop(str(item_id), None)
            
            request.session["cart"] = cart
            
    return redirect("cart")