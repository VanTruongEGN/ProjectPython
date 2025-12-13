from django.shortcuts import render, get_object_or_404
from .models import Product, ProductDiscount, Category



def product_page(request,category_name):
    tablet_category = Category.objects.filter(name__iexact=category_name).first()

    products = Product.objects.filter(category=tablet_category, status=True)
    discounts = ProductDiscount.objects.all()
    discount_map = {d.product.id: d for d in discounts}

    return render(request, 'products/product.html', {
        'products': products,
        'discount_map': discount_map
    })



