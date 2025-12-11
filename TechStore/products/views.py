from django.shortcuts import render
from .models import Product, ProductDiscount, Category

def product_list(request):
    products = Product.objects.filter(status=True).select_related('category').prefetch_related('images')

    discounts = ProductDiscount.objects.all()
    # Map theo product.id (chuỗi "SP001", "SP002", ...)
    discount_map = {d.product.id: d for d in discounts}

    return render(request, 'products/tablet.html', {
        'products': products,
        'discount_map': discount_map
    })


def tablet_page(request):
    tablet_category = Category.objects.filter(name__iexact="Tablet").first()

    products = Product.objects.filter(category=tablet_category, status=True)
    discounts = ProductDiscount.objects.all()
    discount_map = {d.product.id: d for d in discounts}

    return render(request, 'products/tablet.html', {
        'products': products,
        'discount_map': discount_map
    })

def laptop_page(request):
    laptop_category = Category.objects.filter(name__iexact="Laptop").first()
    products = Product.objects.filter(category=laptop_category, status=True)
    discounts = ProductDiscount.objects.all()
    discount_map = {d.product.id: d for d in discounts}

    return render(request, 'products/laptop.html', {
        'products': products,
        'discount_map': discount_map
    })



