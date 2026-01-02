import datetime

from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.hashers import make_password
from django.db import IntegrityError, transaction
from .models import Customer, CartItem, Address, Cart
from django.contrib.auth.hashers import check_password
from accounts.services import merge_session_cart_to_db, get_or_create_user_cart
from .models import Customer, CartItem, Address
from django.contrib.auth.hashers import check_password
from accounts.services import merge_session_cart_to_db, get_or_create_user_cart
from products.models import Product
from orders.models import Order, OrderItem, Payment
from shippings.models import ShippingPartner, OrderShipping
from accounts.models import Address
from django.utils import timezone
from decimal import Decimal
from stores.models import StoreInventory, StoreReservation
from promotions.services import PromotionEngine
from django.db.models import F
from django.contrib import messages
from django.contrib.auth.decorators import login_required
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
    addresses = Address.objects.filter(customer=customer)

    if request.method == "POST":
        customer.full_name = request.POST.get("full_name")
        customer.phone = request.POST.get("phone")
        customer.date_of_birth = request.POST.get("date_of_birth")
        customer.gender = request.POST.get("gender")
        customer.save()

    return render(request, "accounts/profile.html", {
        "customer": customer,
        "addresses": addresses,
        "active_section": "profile"
    })


def logout_view(request):
    request.session.flush()
    return redirect("login")

@transaction.atomic
def process_checkout(request):
    print("=== PROCESS_CHECKOUT START ===")

    if request.method != "POST":
        print("❌ Method != POST")
        return redirect("cart")

    payment_method = request.POST.get("payment_method", "COD")
    print("Payment method:", payment_method)

    # ===== CUSTOMER =====
    if request.session.get("customer_id"):
        customer = Customer.objects.get(id=request.session["customer_id"])
        print("Customer logged in:", customer.id, customer.email)
    else:
        email = request.POST.get("guest_email")
        print("Guest email:", email)

        if not email:
            print("❌ Guest nhưng không có email → redirect login")
            return redirect("login")

        customer, created = Customer.objects.get_or_create(
            email=email,
            defaults={
                "full_name": request.POST.get("recipient_name"),
                "phone": request.POST.get("phone"),
                "password_hash": make_password("guest@123")
            }
        )
        print("Guest customer:", customer.id, "created:", created)
        merge_session_cart_to_db(request, customer)

    # ===== CART =====
    cart = get_or_create_user_cart(customer)
    cart_items = CartItem.objects.filter(cart=cart)

    print("Cart items count:", cart_items.count())
    if not cart_items.exists():
        print("❌ Cart rỗng")
        return redirect("cart")

    from promotions.services import PromotionEngine
    cart_totals = PromotionEngine.calculate_cart_totals(cart_items)
    total = cart_totals["total_final"]
    print("Cart total:", total)

    # ===== ADDRESS =====
    address = Address.objects.create(
        customer=customer,
        recipient_name=request.POST.get("recipient_name"),
        phone=request.POST.get("phone"),
        address_line=request.POST.get("address_line"),
        city=request.POST.get("city", ""),
        district=request.POST.get("district", ""),
        ward=request.POST.get("ward", "")
    )
    print("Address created:", address.id)

    # ===== PAYMENT =====
    payment = Payment.objects.create(
        method=payment_method,
        amount=total,
        status="Chưa thanh toán"
    )
    print("Payment created:", payment.id, payment.method)

    status_map = {
        "COD": "Đang xử lý",
        "BANK": "Chờ xác nhận chuyển khoản",
        "VNPAY": "Chờ thanh toán",
    }

    order = Order.objects.create(
        customer=customer,
        address=address,
        payment=payment,
        total_amount=total,
        shipping_cost=0,
        status=status_map[payment_method],
        note=request.POST.get("note", "")
    )
    print("Order created:", order.id)

    # ===== ORDER ITEMS =====
    items_map = {i["item_id"]: i for i in cart_totals["items_details"]}
    for item in cart_items:
        d = items_map[item.id]
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            unit_price=d["final_single_price"],
            discount_amount=d["original_single_price"] - d["final_single_price"]
        )
        print("OrderItem added:", item.product.name)

    # ===== PAYMENT FLOW =====
    if payment_method == "VNPAY":
        request.session["vnpay_order_id"] = order.id
        print("➡ Redirect to VNPAY | order_id:", order.id)
        return redirect("create_vnpay_payment")

    cart_items.delete()
    print("Cart cleared (non-VNPAY)")
    return redirect("home")


import hmac
import hashlib
import urllib.parse
from datetime import datetime, timedelta
from django.conf import settings
from django.shortcuts import redirect, render
from orders.models import Order

def _normalize_vnp_value(v: str) -> str:
    return str(v).strip()


from .vnpay import VNPay  # Giả sử bạn để class trong file vnpay.py


def create_vnpay_payment(request):
    print("=== CREATE_VNPAY_PAYMENT ===")

    order_id = request.session.get("vnpay_order_id")
    print("Session order_id:", order_id)

    if not order_id:
        print("❌ Không có order_id trong session")
        return redirect("cart")

    order = Order.objects.get(id=order_id)
    print("Order:", order.id, "amount:", order.total_amount)

    vnp = VNPay(
        tmn_code=settings.VNPAY_TMN_CODE,
        hash_secret=settings.VNPAY_HASH_SECRET,
        payment_url=settings.VNPAY_URL,
        return_url=settings.VNPAY_RETURN_URL
    )

    payment_url = vnp.create_payment_url(
        request,
        order_id=order.id,
        amount=order.total_amount,
        order_desc=f"Thanh toan don hang {order.id}"
    )

    print("VNPAY URL:")
    print(payment_url)

    return redirect(payment_url)



def clear_cart(customer):
    try:
        cart = Cart.objects.get(customer=customer)
        cart.cartitem_set.all().delete()
    except Cart.DoesNotExist:
        pass

from django.conf import settings
from django.shortcuts import redirect
import hmac, hashlib

from django.shortcuts import redirect
from django.contrib import messages
from django.conf import settings
import hmac
import hashlib

from orders.models import Order
from accounts.models import CartItem


def vnpay_return(request):
    print("=== VNPAY_RETURN ===")
    print("RAW QUERY:", request.GET.dict())

    vnp_response_code = request.GET.get("vnp_ResponseCode")
    order_id = request.GET.get("vnp_TxnRef")
    vnp_secure_hash = request.GET.get("vnp_SecureHash")

    if not all([vnp_response_code, order_id, vnp_secure_hash]):
        print("❌ Missing params")
        return redirect("home")

    # ===== VERIFY HASH (ĐÚNG CHUẨN VNPAY) =====
    input_data = request.GET.dict()
    input_data.pop("vnp_SecureHash", None)
    input_data.pop("vnp_SecureHashType", None)

    # ⚠️ SORT + URLENCODE (QUAN TRỌNG)
    sorted_items = sorted(input_data.items())
    encoded_query = urllib.parse.urlencode(sorted_items)

    calc_hash = hmac.new(
        settings.VNPAY_HASH_SECRET.encode(),
        encoded_query.encode(),
        hashlib.sha512
    ).hexdigest()

    print("ENCODED QUERY:", encoded_query)
    print("CALC HASH:", calc_hash)
    print("VNP HASH :", vnp_secure_hash)

    if calc_hash != vnp_secure_hash:
        print("❌ HASH NOT MATCH")
        return redirect("home")

    # ===== LẤY ĐƠN =====
    order = Order.objects.select_related("payment").get(id=order_id)

    if vnp_response_code == "00":
        print("✅ PAYMENT SUCCESS")

        order.status = "Đã thanh toán"
        order.payment.status = "Đã thanh toán"
        order.payment.transaction_id = request.GET.get("vnp_TransactionNo")
        order.payment.save()
        order.save()

        # 🔥 PHỤC HỒI SESSION (CỰC KỲ QUAN TRỌNG)
        request.session["customer_id"] = order.customer.id
        request.session["customer_email"] = order.customer.email

        CartItem.objects.filter(cart__customer=order.customer).delete()
        print("🗑 Cart cleared")

        return redirect("home")


    print("❌ PAYMENT FAILED:", vnp_response_code)
    order.status = "Thanh toán thất bại"
    order.payment.status = "Thất bại"
    order.payment.save()
    order.save()

    return redirect("cart")






def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    qty = int(request.POST.get("quantity", 1))

    price_at_add = product.price

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
    total = Decimal(0)

    # Nếu đã đăng nhập thì lấy giỏ hàng từ DB
    if request.session.get("customer_id"):
        customer = Customer.objects.get(id=request.session["customer_id"])
        cart = get_or_create_user_cart(customer)
        cart_items = CartItem.objects.filter(cart=cart).select_related("product")

        cart_totals = PromotionEngine.calculate_cart_totals(cart_items)
        total = cart_totals['total_final']
        total_original = cart_totals['total_original']
        total_discount = cart_totals['total_discount_amount']
        
        for detail in cart_totals['items_details']:
             items.append({
                "id": detail['item_id'],
                "product": detail['product'],
                "quantity": detail['quantity'],
                "price": detail['final_single_price'],
                "original_price": detail['original_single_price'],
                "line_total": detail['line_total'],
                "promotion_rule": detail['applied_rule']
            })


    else:
        # Nếu chưa đăng nhập thì lấy giỏ hàng từ session
        session_cart = request.session.get("cart", {})
        
        mock_items = []
        if session_cart:
            products = Product.objects.filter(id__in=session_cart.keys())
            product_map = {str(p.id): p for p in products}
            
            class MockCartItem:
                def __init__(self, product, quantity):
                    self.id = product.id
                    self.product = product
                    self.quantity = quantity
            
            for pid, data in session_cart.items():
                if pid in product_map:
                    mock_items.append(MockCartItem(product_map[pid], data['qty']))
        
        cart_totals = PromotionEngine.calculate_cart_totals(mock_items)
        
        total = cart_totals['total_final']
        total_original = cart_totals['total_original']
        total_discount = cart_totals['total_discount_amount']

        # Build items list with promo info
        items = []
        for detail in cart_totals['items_details']:
             items.append({
                "id": detail['item_id'],
                "product": detail['product'],
                "quantity": detail['quantity'],
                "price": detail['final_single_price'], 
                "original_price": detail['original_single_price'],
                "line_total": detail['line_total'],
                "promotion_rule": detail['applied_rule']
            })

    # Lấy địa chỉ mặc định hoặc địa chỉ đầu tiên
    user_address = None
    addresses = []
    if request.session.get("customer_id"):
        customer_id = request.session["customer_id"]
        user_address = Address.objects.filter(
            customer_id=customer_id,
            is_default=True
        ).first() or Address.objects.filter(
            customer_id=customer_id
        ).first()
        addresses = Address.objects.filter(customer_id=customer_id)

    # Lấy danh sách đơn vị vận chuyển
    shipping_partners = ShippingPartner.objects.filter(is_active=True)

    return render(request, "accounts/cart.html", {
        "items": items,
        "total": total,
        "total_original": total_original,
        "total_discount": total_discount,
        "user_address": user_address,
        "addresses": addresses,
        "shipping_partners": shipping_partners
    })


def buy_now(request, product_id):
    if request.method != "POST":
        return redirect("productDetail", pk=product_id)

    product = get_object_or_404(Product, id=product_id)
    qty = int(request.POST.get("quantity", 1))
    
    # Discount is now calculated dynamically in Cart
    price_at_add = product.price
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
            messages.error(request, "Mật khẩu hiện tại không đúng.")
            return redirect("profile_password")

        if new_password != confirm_password:
            messages.error(request, "Mật khẩu xác nhận không khớp.")
            return redirect("profile_password")

        customer.password_hash = make_password(new_password)
        customer.save()
        messages.success(request, "Đổi mật khẩu thành công!")
        return redirect("profile_password")

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

def profile_address_view(request):
    customer_id = request.session.get("customer_id")
    if not customer_id:
        return redirect("login")

    customer = Customer.objects.get(id=customer_id)
    error = None
    success = None

    if request.method == "POST":
        try:
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
            success = "Thêm địa chỉ thành công."
        except Exception as e:
            error = f"Lỗi khi thêm địa chỉ: {e}"

    addresses = Address.objects.filter(customer=customer)

    return render(request, "accounts/profile.html", {
        "customer": customer,
        "addresses": addresses,
        "active_section": "address",
        "error": error,
        "success": success,
    })

def profile_orders(request):
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('login')

    customer = Customer.objects.get(id=customer_id)

    # Đơn chưa huỷ
    orders = Order.objects.filter(
        customer=customer
    ).exclude(status="Đã huỷ").order_by('-order_date')

    # Đơn đã huỷ
    cancelled_orders = Order.objects.filter(
        customer=customer,
        status="Đã huỷ"
    ).order_by('-order_date')

    # Gán items + địa chỉ cho từng đơn
    for order in orders:
        order.items = OrderItem.objects.filter(order=order)
        order.shipping_info = Address.objects.filter(order=order).first()

    for order in cancelled_orders:
        order.items = OrderItem.objects.filter(order=order)
        order.shipping_info = Address.objects.filter(order=order).first()

    return render(request, 'accounts/profile.html', {
        'customer': customer,
        'orders': orders,
        'cancelled_orders': cancelled_orders,
        'order_count': orders.count(),
        'active_section': 'orders'
    })

from django.shortcuts import get_object_or_404

def delete_address(request, address_id):
    customer_id = request.session.get("customer_id")
    if not customer_id:
        return redirect("login")

    customer = Customer.objects.get(id=customer_id)
    address = get_object_or_404(Address, id=address_id, customer=customer)

    address.delete()

    addresses = Address.objects.filter(customer=customer)
    return render(request, "accounts/profile.html", {
        "customer": customer,
        "addresses": addresses,
        "active_section": "address",
        "success": "Xóa địa chỉ thành công."
    })

def set_default_address(request, address_id):
    customer_id = request.session.get("customer_id")
    if not customer_id:
        return redirect("login")

    customer = Customer.objects.get(id=customer_id)
    address = get_object_or_404(Address, id=address_id, customer=customer)

    # Bỏ mặc định ở các địa chỉ khác
    Address.objects.filter(customer=customer, is_default=True).update(is_default=False)

    # Đặt địa chỉ này làm mặc định
    address.is_default = True
    address.save()

    addresses = Address.objects.filter(customer=customer)
    return render(request, "accounts/profile.html", {
        "customer": customer,
        "addresses": addresses,
        "active_section": "address",
        "success": "Đã đặt địa chỉ mặc định thành công."
    })
# huỷ đơn hàng
def cancel_order(request, order_id):
    customer_id = request.session.get("customer_id")
    if not customer_id:
        return redirect("login")

    order = get_object_or_404(Order, id=order_id, customer_id=customer_id)

    # chỉ cho huỷ khi đang xử lý
    if order.status == "Đang xử lý":
        order.status = "Đã huỷ"
        order.save()
        messages.success(request, "Đã huỷ đơn hàng thành công")

    return redirect("profile_orders")
def profile_cancelled_orders(request):
    customer_id = request.session.get("customer_id")
    if not customer_id:
        return redirect("login")

    customer = Customer.objects.get(id=customer_id)

    cancelled_orders = Order.objects.filter(
        customer=customer,
        status="Đã huỷ"
    ).order_by("-order_date")

    return render(request, "accounts/profile.html", {
        "customer": customer,
        "cancelled_orders": cancelled_orders,
        "active_section": "cancelled_orders",
        "order_count": cancelled_orders.count(),
    })


def get_logged_in_customer(request):
    customer_id = request.session.get("customer_id")
    if not customer_id:
        return None
    return Customer.objects.filter(id=customer_id).first()

