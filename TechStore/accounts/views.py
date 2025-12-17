from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from django.db import IntegrityError

from orders.models import Order
from .models import Customer, Address
from django.contrib.auth.hashers import check_password

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
                request.session["customer_id"] = customer.id
                request.session["customer_email"] = customer.email
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
    })

def logout_view(request):
    request.session.flush()
    return redirect("login")

from datetime import datetime

def update_profile(request):
    customer_id = request.session.get("customer_id")
    if not customer_id:
        return redirect("login")

    customer = Customer.objects.get(id=customer_id)

    if request.method == "POST":
        customer.full_name = request.POST.get("fullName")
        customer.phone = request.POST.get("phoneNumber")
        customer.gender = request.POST.get("gender")

        # Lấy ngày sinh từ input
        dob_str = request.POST.get("date_of_birth")
        if dob_str:
            try:
                customer.date_of_birth = datetime.strptime(dob_str, "%Y-%m-%d").date()
            except ValueError:
                pass  # nếu format sai thì bỏ qua

        customer.save()
        return redirect("profile")

    return render(request, "accounts/edit_profile.html", {"customer": customer})

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