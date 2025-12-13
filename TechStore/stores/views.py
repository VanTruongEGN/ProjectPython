# Create your views here.
# stores/views.py

from django.shortcuts import render
def home(request):
    images = [
        "stores/images/img1.png",
        "stores/images/img2.png",
        "stores/images/img3.png",
    ]
    return render(request, 'store/home.html', {"images": images})
#products
def tablet_page(request):
    return render(request, 'products/tablet.html')

def laptop_page(request):
    return render(request, 'products/product.html')

def phukien_page(request):
    return render(request, 'products/phukien.html')

def mouse_page(request):
    return render(request, 'products/mouse.html')

def keyboard_page(request):
    return render(request, 'products/keyboard.html')

def mayin_page(request):
    return render(request, 'products/mayin.html')

def manhinh_page(request):
    return render(request, 'products/manhinh.html')

#accounts
def login_page(request):
    return render(request, 'accounts/login.html')

def register_page(request):
    return render(request, 'accounts/register.html')

def personal_page(request):
    return render(request, 'accounts/personal-page.html')







