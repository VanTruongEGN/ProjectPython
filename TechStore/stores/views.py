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

def tablet_page(request):
    return render(request, 'includes/tablet.html')
def keyboard(request):
    return render(request, 'includes/keyboard.html')
def laptop(request):
    return render(request, 'includes/laptop.html')
def manhinh(request):
    return render(request, 'includes/manhinh.html')
def mayin(request):
    return render(request, 'includes/mayin.html')
def mouse(request):
    return render(request, 'includes/mouse.html')
def phukien(request):
    return render(request, 'includes/phukien.html')
def register(request):
    return render(request, 'includes/register.html')
def personal(request):
    return render(request, 'includes/personal-page.html')
