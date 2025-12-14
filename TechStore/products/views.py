from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from .models import Product, ProductDiscount, Category, ProductAttribute


def product_page(request,category_name):
    tablet_category = Category.objects.filter(name__iexact=category_name).first()

    products = Product.objects.filter(category=tablet_category, status=True)
    discounts = ProductDiscount.objects.all()
    discount_map = {d.product.id: d for d in discounts}

    return render(request, 'products/product.html', {
        'products': products,
        'discount_map': discount_map
    })

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, status=True)

    # Ảnh
    images = product.images.all()
    main_image = product.image_main or (images.first().image if images else None)

    # Thông số kỹ thuật
    attributes = ProductAttribute.objects.filter(product=product)

    # Khuyến mãi
    discount = ProductDiscount.objects.filter(
        product=product,
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now()
    ).first()

    return render(request, 'products/productDetails.html', {
        'product': product,
        'images': images,
        'main_image': main_image,
        'attributes': attributes,
        'discount': discount
    })

