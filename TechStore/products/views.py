import io
import math
from datetime import datetime

import numpy as np
from django.core.paginator import Paginator
from django.db.models import Avg, Q, Count
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
import matplotlib
from matplotlib.ticker import MaxNLocator

matplotlib.use('Agg')
import matplotlib.pyplot as plt

from accounts.models import Customer, Address
from comments.models import Comment
from sentiment.services import predict_sentiment
from .models import Product, Category, ProductAttribute
from promotions.services import PromotionEngine
from orders.models import OrderItem
from orders.utils import has_purchased_product
def product_page(request,category_name):
    images = ["products/images/img1.png", "products/images/img2.png", "products/images/img3.png"]
    category = Category.objects.filter(name__iexact=category_name).first()

    products = Product.objects.filter(category=category, status=True)

    paginator = Paginator(products, 10)
    pageNumber = request.GET.get('page')
    pageObj = paginator.get_page(pageNumber)

    discountMap = {}
    for p in pageObj:
        price, rule, orig = PromotionEngine.calculate_best_price(p)
        if rule:
             class DiscountObj: 
                 def __init__(self, p, pr, o):
                     self.discounted_price = pr
                     self.original_price = o
                     self.product = p
                 def formatted_priceD(self): return f"{int(self.discounted_price):,} VNĐ".replace(",", ".")
                 def formatted_price(self): return f"{int(self.original_price):,} VNĐ".replace(",", ".")

             discountMap[p.id] = DiscountObj(p, price, orig)

    return render(request, 'products/product.html', {
        'products': products,
        'discount_map': discountMap,
        'images': images,
        'pageObj': pageObj,
    })

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, status=True)
    ratingAVG = Comment.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg'] or 0
    ratingAVG_int = math.floor(ratingAVG)
    images = product.images.all()
    main_image = product.image_main or (images.first().image if images else None)

    # Thông số kỹ thuật
    attributes = ProductAttribute.objects.filter(product=product)

    # Khuyến mãi
    price, rule, orig_price = PromotionEngine.calculate_best_price(product)
    discount = None
    if rule:
        class DiscountObj:
             def __init__(self, p, pr, o):
                 self.discounted_price = pr
                 self.original_price = o
             def formatted_priceD(self): return f"{int(self.discounted_price):,} VNĐ".replace(",", ".")
        discount = DiscountObj(product, price, orig_price)


    comments = Comment.objects.filter(product=product).order_by('-created_at')
    rating = request.GET.get('rating')
    if rating:
        comments = comments.filter(rating=rating)
    # thống kê số sao
    rating_stats = (
            Comment.objects
            .filter(product=product)
            .values('rating')
            .annotate(total=Count('id'))
        )

    rating_count = {i: 0 for i in range(1, 6)}
    for r in rating_stats:
        rating_count[r['rating']] = r['total']

    # check đã mua hàng chưa
    customer = None
    can_comment = False
    has_commented = False

    customer_id = request.session.get("customer_id")
    if customer_id:
        customer = Customer.objects.filter(id=customer_id).first()
        if customer:
            has_commented = Comment.objects.filter(
                customer=customer,
                product=product
            ).exists()

            if has_purchased_product(customer, product) and not has_commented:
                can_comment = True

    return render(request, 'products/productDetails.html', {
        'product': product,
    'images': images,
    'main_image': main_image,
    'attributes': attributes,
    'discount': discount,
    'comments': comments,
    'ratingAVG': ratingAVG_int,
    'ajax': True,
    'can_comment': can_comment,
    'has_commented': has_commented,
    'rating_count': rating_count,
    })

def addComment(request, pk):
    if request.method != "POST":
        return redirect('productDetail', pk=pk)

    customer_id = request.session.get("customer_id")
    if not customer_id:
        return redirect('login')

    customer = get_object_or_404(Customer, id=customer_id)
    product = get_object_or_404(Product, id=pk)

    # CHECK ĐÃ MUA TRƯỚC
    if not has_purchased_product(customer, product):
        return JsonResponse(
            {"error": "Bạn phải mua sản phẩm này trước khi đánh giá"},
            status=403
        )

    content = request.POST.get("content")
    rating = request.POST.get("rating")

    if not content or not rating:
        return redirect('productDetail', pk=pk)

    result = predict_sentiment(content)
    label = result["label"]

    # CHỈ TẠO COMMENT SAU KHI ĐÃ CHECK
    if Comment.objects.filter(customer=customer, product=product).exists():
        return redirect('productDetail', pk=pk)
    Comment.objects.create(
        customer=customer,
        product=product,
        content=content,
        rating=rating,
        label=label,
    )

    comments = Comment.objects.filter(product=product).order_by('-created_at')

    return render(request, 'products/productDetails.html', {
        'product': product,
        'comments': comments,
        'ajax': True
    })

def product_list(request):
    images = ["products/images/img1.png", "products/images/img2.png", "products/images/img3.png"]

    keyword = request.GET.get("q", "").strip()
    now = timezone.now()

    products = Product.objects.all()

    if keyword:
        products = products.filter(
            Q(name__icontains=keyword)
        )

    paginator = Paginator(products, 10)
    pageNumber = request.GET.get('page')
    pageObj = paginator.get_page(pageNumber)

    # Fix Logic: Calculate discounts for products in the current page
    discount_map = {}
    for p in pageObj:
         price, rule, orig = PromotionEngine.calculate_best_price(p)
         if rule:
             class DiscountObj:
                 def __init__(self, p, pr, o):
                     self.product_id = p.id
                     self.discounted_price = pr
                     self.original_price = o
                 def formatted_priceD(self): return f"{int(self.discounted_price):,} VNĐ".replace(",", ".")
                 def formatted_price(self): return f"{int(self.original_price):,} VNĐ".replace(",", ".")
             discount_map[p.id] = DiscountObj(p, price, orig)
             
    # Clean up unused code
    discounts = []




    return render(request, "products/product.html", {
        "products": products,
        "discount_map": discount_map,
        "keyword": keyword,
        "images": images,
        "pageObj": pageObj,
    })

def add_address(request):
    customer_id = request.session.get("customer_id")
    if not customer_id:
        return redirect("login")

    customer = Customer.objects.get(id=customer_id)

    if request.method == "POST":
        Address.objects.create(
            customer=customer,
            recipient_name=request.POST.get("recipient_name"),
            phone=request.POST.get("phone"),  # nhớ đồng bộ name trong form
            address_line=request.POST.get("address_line"),
            ward=request.POST.get("ward"),
            district=request.POST.get("district"),
            city=request.POST.get("city"),
            postal_code=request.POST.get("postal_code"),
            is_default=request.POST.get("is_default") == "on"
        )
        return redirect("profile")

    return render(request, "accounts/add_addresses.html")

def delete_address(request, address_id):
    customer_id = request.session.get("customer_id")
    if not customer_id:
        return redirect("login")

    if request.method == "POST":
        Address.objects.filter(id=address_id, customer_id=customer_id).delete()
    return redirect("profile")


