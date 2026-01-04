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
from spam_detector.services.comment_pipeline import process_comment

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

    return render(request, 'products/productDetails.html', {
        'product': product,
        'images': images,
        'main_image': main_image,
        'attributes': attributes,
        'discount': discount,
        'comments': comments,
        'ratingAVG': ratingAVG_int,
        'ajax': True,
    })

SPAM_THRESHOLD = 0.7

def addComment(request, pk):
    if request.method != "POST":
        return redirect('productDetail', pk=pk)

    customer_id = request.session.get("customer_id")
    if not customer_id:
        return redirect('login')

    content = request.POST.get("content")
    rating = request.POST.get("rating") or 5

    if not content:
        return redirect('productDetail', pk=pk)

    customer = get_object_or_404(Customer, id=customer_id)
    product = get_object_or_404(Product, id=pk)

    # ===== comment pipeline (spam + sentiment) =====
    res = process_comment(content)
    is_spam = res.get("is_spam", False)
    spam_score = res.get("spam_prob", 0)
    if res.get("spam_source") == "rule":
        spam_score = 1.0

    label = None
    if not is_spam:
        label = res.get("sentiment", {}).get("label")

    Comment.objects.create(
        customer=customer,
        product=product,
        content=content,
        rating=rating,
        is_spam=is_spam,
        spam_score=spam_score,
        label=label,
    )

    comments = Comment.objects.filter(product=product).order_by('-created_at')

    # ===== AJAX: render FULL PAGE =====
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return render(request, "products/productDetails.html", {
            "product": product,
            "comments": comments,
            "ajax": True,
        })

    return redirect('productDetail', pk=pk)

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

def review_chart(request, pk):
    product = get_object_or_404(Product, pk=pk, status=True)

    # Thống kê theo label
    review_counts = Comment.objects.filter(product=product).values('label').annotate(count=Count('id'))
    counts = {'tích cực': 0, 'tiêu cực': 0}
    for item in review_counts:
        counts[item['label']] = item['count']

    # Vẽ biểu đồ
    labels = ['Tích cực', 'Tiêu cực']
    values = [counts['tích cực'], counts['tiêu cực']]
    colors = ['#4ADE80', '#F87171']

    ax = plt.gca()
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))

    plt.figure(figsize=(6,4))
    plt.bar(labels, values, color=colors)
    plt.title('Thống kê lượt đánh giá')
    plt.ylim(0, max(values)*1.2)
    plt.ylabel('Số lượt đánh giá')

    # Lưu ảnh vào buffer
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return HttpResponse(buf.getvalue(), content_type='image/png')
