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
def register(request):
    return render(request, 'includes/register.html')
def personal(request):
    return render(request, 'includes/personal-page.html')
