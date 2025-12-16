# Create your views here.
# stores/views.py
from django.shortcuts import render

from products.models import ProductDiscount, ProductImage, Category, ProductAttribute


def home(request):
    images = ["store/images/img1.png", "store/images/img2.png", "store/images/img3.png"]
    categories = Category.objects.all()

    discount_by_category = {}

    for cat in categories:
        discounts = (
            ProductDiscount.objects
            .select_related('product', 'product__category')
            .filter(
                product__category=cat,
                product__status=True,
            )
            .order_by('-created_at')[:8]
        )
        for d in discounts:
            d.attrs = ProductAttribute.objects.filter(
                product=d.product
            )[:2]

        if discounts.exists():
            discount_by_category[cat] = discounts

    return render(request, 'store/home.html', {
        'discount_by_category': discount_by_category,
        'images': images
    })

#accounts
def login_page(request):
    return render(request, 'accounts/login.html')

def register_page(request):
    return render(request, 'accounts/signup.html')

def personal_page(request):
    return render(request, 'accounts/personal-page.html')







