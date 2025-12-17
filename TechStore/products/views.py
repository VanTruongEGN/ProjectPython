import math
from datetime import datetime

from django.db.models import Avg, Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from accounts.models import Customer
from comments.models import Comment
from .models import Product, ProductDiscount, Category, ProductAttribute


def product_page(request,category_name):
    images = ["products/images/img1.png", "products/images/img2.png", "products/images/img3.png"]
    tablet_category = Category.objects.filter(name__iexact=category_name).first()

    products = Product.objects.filter(category=tablet_category, status=True)
    discounts = ProductDiscount.objects.filter(end_date__gte=timezone.now()).order_by("end_date")
    discount_map = {d.product.id: d for d in discounts}

    return render(request, 'products/product.html', {
        'products': products,
        'discount_map': discount_map,
        'images': images,
    })

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, status=True)
    comment = Comment.objects.filter(product=product).order_by('-created_at')
    ratingAVG = Comment.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg'] or 0
    ratingAVG_int = math.floor(ratingAVG)
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
        'discount': discount,
        'comment': comment,
        'ratingAVG': ratingAVG_int,
    })
def addComment(request, pk):
    if request.method != "POST":
        return redirect('productDetail', pk=pk)

    customer_id = request.session.get("customer_id")
    if not customer_id:
        return redirect('login')  # nếu chưa login

    content = request.POST.get("content")
    rating = request.POST.get("rating")

    if not content:
        # có thể thêm message báo lỗi
        return redirect('productDetail', pk=pk)

    customer = get_object_or_404(Customer, id=customer_id)
    product = get_object_or_404(Product, id=pk)

    Comment.objects.create(
        customer=customer,
        product=product,
        content=content,
        rating=rating,
        created_at=datetime.now().strftime("%d/%m/%Y"),
    )

    return redirect('productDetail', pk=pk)

def product_list(request):
    images = ["products/images/img1.png", "products/images/img2.png", "products/images/img3.png"]

    keyword = request.GET.get("q", "").strip()
    now = timezone.now()

    products = Product.objects.all()

    if keyword:
        products = products.filter(
            Q(name__icontains=keyword) |
            Q(description__icontains=keyword)
        )

    discounts = ProductDiscount.objects.filter(
        start_date__lte=now,
        end_date__gte=now,
        product__in=products
    )

    discount_map = {}
    for d in discounts:
        if d.product_id not in discount_map:
            discount_map[d.product_id] = d

    return render(request, "products/product.html", {
        "products": products,
        "discount_map": discount_map,
        "keyword": keyword,
        "images": images,
    })

