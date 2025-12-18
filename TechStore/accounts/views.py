import datetime

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
from shippings.models import ShippingPartner, OrderShipping
from accounts.models import Address
from django.utils import timezone
from decimal import Decimal
from stores.models import StoreInventory, StoreReservation
from django.db.models import F

def signup_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        full_name = request.POST.get("full_name")
        phone = request.POST.get("phone")
        date_of_birth = request.POST.get("date_of_birth")
        gender = request.POST.get("gender")


        if password != confirm_password:
            return render(request, "accounts/signup.html", {
                "error": "Mật khẩu xác nhận không khớp."
            })


        if Customer.objects.filter(email=email).exists():
            return render(request, "accounts/signup.html", {
                "error": "Email đã được sử dụng."
            })


        password_hash = make_password(password)

        customer = Customer(
            email=email,
            password_hash=password_hash,
            full_name=full_name,
            phone=phone,
            date_of_birth=date_of_birth if date_of_birth else None,
            gender=gender,
        )
        customer.save()
        return redirect("login")

    return render(request, "accounts/signup.html")




def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            customer = Customer.objects.get(email=email)
            if check_password(password, customer.password_hash):
                request.session["customer_id"] = str(customer.id)
                request.session["customer_email"] = customer.email
                merge_session_cart_to_db(request, customer)
                return redirect("profile")
            else:
                error = "Sai mật khẩu. Vui lòng thử lại."
        except Customer.DoesNotExist:
            error = "Email không tồn tại."

        return render(request, "accounts/login.html", {"error": error})
    return render(request, "accounts/login.html")
def profile_view(request):
    customer_id = request.session.get("customer_id")
    if not customer_id:
        return redirect("login")

    customer = Customer.objects.get(id=customer_id)
    order_count = Order.objects.filter(customer=customer).count()
    addresses = Address.objects.filter(customer=customer)

    return render(request, "accounts/profile.html", {
        "customer": customer,
        "order_count": order_count,
        "addresses": addresses,
        "active_section": "profile",
    })

def logout_view(request):
    request.session.flush()
    return redirect("login")

@transaction.atomic
def process_checkout(request):
    if request.method != "POST":
        return redirect("cart")

    customer = None
    if request.session.get("customer_id"):
        customer = Customer.objects.get(id=request.session["customer_id"])
    else:
        email = request.POST.get("guest_email")
        if not email:
            return redirect("login") 
        
        customer = Customer.objects.filter(email=email).first()
        if not customer:
            customer = Customer(
                email=email,
                full_name=request.POST.get("recipient_name"),
                phone=request.POST.get("phone"),
                password_hash=make_password("guest@123")
            )
            customer.save()
        
        merge_session_cart_to_db(request, customer)

    cart = get_or_create_user_cart(customer)
    cart_items = CartItem.objects.filter(cart=cart).select_related("product")
    
    if not cart_items.exists():
        return redirect("cart")

    total = 0
    for item in cart_items:
        total += item.quantity * item.price_at_add

    address = None
    delivery_method = request.POST.get("delivery_method", "home")
    pickup_store = None

    if delivery_method == "home":
        address_id = request.POST.get("address_id")
        
        if address_id:
            address = Address.objects.filter(id=address_id, customer=customer).first()
        if not address:
            recipient_name = request.POST.get("recipient_name")
            phone = request.POST.get("phone")
            address_line = request.POST.get("address_line")
            city = request.POST.get("city")
            district = request.POST.get("district")
            ward = request.POST.get("ward")

            if recipient_name and phone and address_line:
                address = Address.objects.create(
                    customer=customer,
                    recipient_name=recipient_name,
                    phone=phone,
                    address_line=address_line,
                    city=city or "",
                    district=district or "",
                    ward=ward or ""
                )
            else:
                address = Address.objects.filter(customer=customer, is_default=True).first() \
                or Address.objects.filter(customer=customer).first()

        if not address:
            return redirect("cart")
            
    elif delivery_method == "store":
        store_id = request.POST.get("pickup_store_id")
        if store_id:
            from stores.models import Store
            pickup_store = Store.objects.filter(id=store_id).first()
        
        if not pickup_store:
            return redirect("cart")


    shipping_partner_id = request.POST.get("shipping_partner")
    shipping_partner = None
    shipping_cost = 0
    if shipping_partner_id:
        try:
             shipping_partner = ShippingPartner.objects.get(id=shipping_partner_id)
             shipping_cost = shipping_partner.price
        except ShippingPartner.DoesNotExist:
             pass

    total_with_shipping = total + shipping_cost

    payment = Payment.objects.create(
        method=request.POST.get("payment_method", "COD"),
        amount=total_with_shipping,
        status="Chưa thanh toán"
    )

    order = Order.objects.create(
        customer=customer,
        address=address,
        payment=payment,
        total_amount=total_with_shipping,
        shipping_cost=shipping_cost,
        status="Đang xử lý",
        note=request.POST.get("note", ""),
        pickup_store_id=pickup_store
    )

    if shipping_partner:
        OrderShipping.objects.create(
            order=order,
            partner=shipping_partner,
            shipping_fee=shipping_cost,
            status="Đang xử lý"
        )
    



    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            unit_price=item.price_at_add
    )

    if delivery_method == "store" and pickup_store:
        inventory = StoreInventory.objects.select_for_update().filter(
            store=pickup_store,
            product=item.product
        ).first()

        if not inventory:
            raise Exception("Không có hàng tại cửa hàng")

        if inventory.stock - inventory.reserved_stock < item.quantity:
            raise Exception("Không đủ hàng")

        inventory.reserved_stock = F("reserved_stock") + item.quantity
        inventory.save(update_fields=["reserved_stock"])

        StoreReservation.objects.create(
            order=order,
            store=pickup_store,
            customer=customer,
            product=item.product,
            quantity=item.quantity,
            status="Pending"
        )



    cart_items.delete()

    if not request.session.get("customer_id"):
        request.session["cart"] = {}
        
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

    from shippings.models import ShippingPartner
    shipping_partners = ShippingPartner.objects.filter(is_active=True)

    return render(request, "accounts/cart.html", {
        "items": items,
        "total": total,
        "user_address": user_address,
        "shipping_partners": shipping_partners
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

def change_password(request):
    customer_id = request.session.get("customer_id")
    if not customer_id:
        return redirect("login")

    customer = Customer.objects.get(id=customer_id)

    if request.method == "POST":
        current_password = request.POST.get("currentPassword")
        new_password = request.POST.get("newPassword")
        confirm_password = request.POST.get("confirmPassword")

        if not check_password(current_password, customer.password_hash):
            return render(request, "accounts/change_password.html", {"error": "Mật khẩu hiện tại không đúng."})

        if new_password != confirm_password:
            return render(request, "accounts/change_password.html", {"error": "Mật khẩu xác nhận không khớp."})

        customer.password_hash = make_password(new_password)
        customer.save()
        return redirect("profile")

    return render(request, "accounts/change_password.html")

def edit_profile(request):
    customer_id = request.session.get("customer_id")
    if not customer_id:
        return redirect("login")

    customer = Customer.objects.get(id=customer_id)

    if request.method == "POST":
        customer.full_name = request.POST.get("fullName")
        customer.phone = request.POST.get("phoneNumber")
        customer.gender = request.POST.get("gender")

        dob_str = request.POST.get("date_of_birth")
        if dob_str:
            try:
                customer.date_of_birth = datetime.strptime(dob_str, "%Y-%m-%d").date()
            except ValueError:
                pass

        customer.save()
        return redirect("profile")

    return render(request, "accounts/edit_profile.html", {"customer": customer})
def profile_password_view(request):
    customer_id = request.session.get("customer_id")
    if not customer_id:
        return redirect("login")

    customer = Customer.objects.get(id=customer_id)
    error = None
    success = None

    if request.method == "POST":
        current_password = request.POST.get("currentPassword")
        new_password = request.POST.get("newPassword")
        confirm_password = request.POST.get("confirmPassword")

        if not check_password(current_password, customer.password_hash):
            error = "Mật khẩu hiện tại không đúng."
        elif new_password != confirm_password:
            error = "Mật khẩu xác nhận không khớp."
        else:
            customer.password_hash = make_password(new_password)
            customer.save()
            success = "Đổi mật khẩu thành công."

    return render(request, "accounts/profile.html", {
        "customer": customer,
        "active_section": "password",
        "error": error,
        "success": success,
    })
def add_address(request):
    customer_id = request.session.get("customer_id")
    if not customer_id:
        return redirect("login")

    customer = Customer.objects.get(id=customer_id)

    if request.method == "POST":
        Address.objects.create(
            customer=customer,
            recipient_name=request.POST.get("recipient_name"),
            phone=request.POST.get("phone"),
            address_line=request.POST.get("address_line"),
            ward=request.POST.get("ward"),
            district=request.POST.get("district"),
            city=request.POST.get("city"),
            postal_code=request.POST.get("postal_code"),
            is_default=request.POST.get("is_default") == "on"
        )
        return redirect("profile")

    return render(request, "accounts/add_addresses.html")

def delete_address(request, address_id):
    customer_id = request.session.get("customer_id")
    if not customer_id:
        return redirect("login")

    if request.method == "POST":
        Address.objects.filter(id=address_id, customer_id=customer_id).delete()
    return redirect("profile")

def profile_address_view(request):
    customer_id = request.session.get("customer_id")
    if not customer_id:
        return redirect("login")

    customer = Customer.objects.get(id=customer_id)
    error = None
    success = None

    if request.method == "POST":
        Address.objects.create(
            customer=customer,
            recipient_name=request.POST.get("recipient_name"),
            phone=request.POST.get("phone"),
            address_line=request.POST.get("address_line"),
            ward=request.POST.get("ward"),
            district=request.POST.get("district"),
            city=request.POST.get("city"),
            is_default=request.POST.get("is_default") == "on"
        )
        success = "Thêm địa chỉ thành công."

    return render(request, "accounts/profile.html", {
        "customer": customer,
        "active_section": "address",  # để template hiển thị section địa chỉ
        "error": error,
        "success": success,
    })
