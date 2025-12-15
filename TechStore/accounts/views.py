from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.hashers import make_password
from django.db import IntegrityError
from .models import Customer
from django.contrib.auth.hashers import check_password
from accounts.services import merge_session_cart_to_db, get_or_create_user_cart
from products.models import Product

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
                request.session["customer_id"] = customer.id
                request.session["customer_email"] = customer.email
                merge_session_cart_to_db(request, customer)
                return redirect("home")  # hoặc trang dashboard
            else:
                error = "Sai mật khẩu. Vui lòng thử lại."
        except Customer.DoesNotExist:
            error = "Email không tồn tại."

        return render(request, "accounts/login.html", {"error": error})
    return render(request, "accounts/login.html")

def checkout_view(request):
    return render(request, "accounts/checkout.html")

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    qty = int(request.POST.get("quantity", 1))
    if request.session.get("customer_id"):
        customer = Customer.objects.get(id=request.session["customer_id"])
        cart = get_or_create_user_cart(customer)

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={"quantity": qty}
        )
        if not created:
            item.quantity += qty
            item.save()
    else:
        cart = request.session.get("cart", {})

        if str(product.id) in cart:
            cart[str(product.id)]["qty"] += qty
        else:
            cart[str(product.id)] = {"qty": qty}

        request.session["cart"] = cart

    return redirect(request.META.get("HTTP_REFERER", "/"))

def cart_view(request):
    items = []
    total = 0

    if request.session.get("customer_id"):
        customer = Customer.objects.get(id=request.session["customer_id"])
        cart = get_or_create_user_cart(customer)

        for item in cart.items.select_related("product"):
            line_total = item.quantity * item.product.price
            total += line_total
            items.append({
                "id": item.id,
                "product": item.product,
                "quantity": item.quantity,
                "price": item.product.price,
                "line_total": line_total,
            })
    else:
        session_cart = request.session.get("cart", {})

        for product_id, data in session_cart.items():
            product = Product.objects.get(id=product_id)
            line_total = data["qty"] * product.price
            total += line_total
            items.append({
                "id": product.id,
                "product": product,
                "quantity": data["qty"],
                "price": product.price,
                "line_total": line_total,
            })

    return render(request, "accounts/cart.html", {
        "items": items,
        "total": total
    })

def buy_now(request, product_id):
    if request.method != "POST":
        return redirect("productDetail", pk=product_id)

    product = get_object_or_404(Product, id=product_id)
    qty = int(request.POST.get("quantity", 1))

    if request.session.get("customer_id"):
        customer = Customer.objects.get(id=request.session["customer_id"])
        cart = get_or_create_user_cart(customer)

        cart.items.all().delete()

        CartItem.objects.create(
            cart=cart,
            product=product,
            quantity=qty
        )


    else:
        request.session["cart"] = {
            str(product.id): {"qty": qty}
        }

    return redirect("checkout")

    
def cart_remove(request, item_id):
    # USER → DB cart
    if request.session.get("customer_id"):
        customer = Customer.objects.get(id=request.session["customer_id"])
        cart = get_or_create_user_cart(customer)
        CartItem.objects.filter(cart=cart, id=item_id).delete()

    # GUEST → session cart
    else:
        cart = request.session.get("cart", {})
        cart.pop(str(item_id), None)
        request.session["cart"] = cart

    return redirect("cart")