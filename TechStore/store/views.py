# Create your views here.
# store/views.py

from django.shortcuts import render
def home(request):
    # Logic xử lý dữ liệu (ví dụ: lấy sản phẩm từ database)
    context = {'title': 'Trang Chủ TechStore', 'welcome_message': 'Chào mừng bạn đến với cửa hàng!'}

    # Trả về một template HTML
    return render(request, 'store/home.html', context)
def carousel(request):
    images=[
        "TechStore/store/img/img1.png"
    ]
    return render(request, 'TechStore/templates/includes/carousel.html')