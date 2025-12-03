# Create your views here.
# store/views.py

from django.shortcuts import render
def home(request):
    images = [
        "store/images/img1.png",
        "store/images/img2.png",
        "store/images/img3.png",
    ]
    return render(request, 'store/home.html', {"images": images})
from django.shortcuts import render

def tablet_page(request):
    return render(request, 'includes/tablet.html')

