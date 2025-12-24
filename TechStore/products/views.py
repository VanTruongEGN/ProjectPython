import io
import math
from datetime import datetime

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
from .models import Product, ProductDiscount, Category, ProductAttribute


def product_page(request,category_name):
    images = ["products/images/img1.png", "products/images/img2.png", "products/images/img3.png"]
    category = Category.objects.filter(name__iexact=category_name).first()

    products = Product.objects.filter(category=category, status=True)

    paginator = Paginator(products, 10)
    pageNumber = request.GET.get('page')
    pageObj = paginator.get_page(pageNumber)

    discounts = ProductDiscount.objects.filter(end_date__gte=timezone.now()).order_by("end_date")
    discountMap = {d.product.id: d for d in discounts}

    return render(request, 'products/product.html', {
        'products': products,
        'discount_map': discountMap,
        'images': images,
        'pageObj': pageObj,
    })

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, status=True)
    comments = Comment.objects.filter(product=product).order_by('-created_at')
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
        'comments': comments,
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
    result = predict_sentiment(content)
    label=result["label"]

    Comment.objects.create(
        customer=customer,
        product=product,
        content=content,
        rating=rating,
        label=label,
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
            Q(name__icontains=keyword)
        )

    paginator = Paginator(products, 10)
    pageNumber = request.GET.get('page')
    pageObj = paginator.get_page(pageNumber)

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