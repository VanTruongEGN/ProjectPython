# Create your views here.
# stores/views.py
from django.shortcuts import render

from products.models import ProductDiscount, ProductImage, Category, ProductAttribute


def home(request):
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
        'discount_by_category': discount_by_category
    })

#accounts
def login_page(request):
    return render(request, 'accounts/login.html')

def register_page(request):
    return render(request, 'accounts/signup.html')

def personal_page(request):
    return render(request, 'accounts/profile.html')







