# Create your views here.
# store/views.py

from django.shortcuts import render
def home(request):
    images = [
        "store/images/img1.png",
        "store/images/img1.png",
        "store/images/img1.png",
    ]
    return render(request, 'store/home.html', {"images": images})
