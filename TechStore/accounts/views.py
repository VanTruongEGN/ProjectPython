from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from django.db import IntegrityError
from .models import Customer
from django.contrib.auth.hashers import check_password


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
                return redirect("home")  # hoặc trang dashboard
            else:
                error = "Sai mật khẩu. Vui lòng thử lại."
        except Customer.DoesNotExist:
            error = "Email không tồn tại."

        return render(request, "accounts/login.html", {"error": error})

    return render(request, "accounts/login.html")
