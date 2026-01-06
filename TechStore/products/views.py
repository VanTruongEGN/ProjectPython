import math
import pickle

from django.core.files.storage import default_storage
from django.core.paginator import Paginator
from django.db.models import Avg, Q, Count
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect

from image_search.yolo.detector import detect_category
from image_search.yolo.image_feature import extract_feature
from image_search.yolo.similarity import calc_similarity


from accounts.models import Customer, Address
from comments.models import Comment
from sentiment.services import predict_sentiment
from .models import Product, Category, ProductAttribute, ProductImage
from promotions.services import PromotionEngine
from orders.models import OrderItem
from orders.utils import has_purchased_product
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
    # thống kê tích cực, tiêu cực
    positive_count = Comment.objects.filter(
        product=product,
        label__iexact='tích cực'
    ).count()

    negative_count = Comment.objects.filter(
        product=product,
        label__iexact='tiêu cực'
    ).count()


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
            purchased_count = OrderItem.objects.filter(
                order__customer=customer,
                product=product,
                order__status__in=['Đã thanh toán', 'hoàn thành']
            ).count()

            comment_count = Comment.objects.filter(
                customer=customer,
                product=product
            ).count()

            if purchased_count > comment_count:
                can_comment = True

            if comment_count > 0:
                has_commented = True


    # lọc theo sao hoặc tích cực / tiêu cực
    filter_value = request.GET.get('filter')

    if filter_value:
        if filter_value.isdigit():  # 1–5 sao
            comments = comments.filter(rating=int(filter_value))
        elif filter_value == 'positive':
            comments = comments.filter(label__iexact='tích cực')
        elif filter_value == 'negative':
            comments = comments.filter(label__iexact='tiêu cực')
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

SPAM_THRESHOLD = 0.7

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
    rating = request.POST.get("rating") or 5
    if not content or not rating:
        return redirect('productDetail', pk=pk)

    result = predict_sentiment(content)
    label = result["label"]

    purchased_count = OrderItem.objects.filter(
        order__customer=customer,
        product=product,
        order__status__in=['Đã thanh toán', 'hoàn thành']
    ).count()

    comment_count = Comment.objects.filter(
        customer=customer,
        product=product
    ).count()

    if comment_count >= purchased_count:
        return JsonResponse(
            {"error": "Bạn đã đánh giá đủ số lần cho sản phẩm này"},
            status=403
        )

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
        label=label,
        is_spam=is_spam,
        spam_score=spam_score,
    )

    comments = Comment.objects.filter(product=product).order_by('-created_at')

    return render(request, 'products/productDetails.html', {
        'product': product,
        'comments': comments,
        'ajax': True
    })

def product_list(request):
    images = [
        "products/images/img1.png",
        "products/images/img2.png",
        "products/images/img3.png",
    ]

    keyword = request.POST.get("q", "").strip()
    upload_image = request.FILES.get("image")

    # Base queryset
    products_qs = Product.objects.filter(status=True)

    if upload_image:
        #  Lưu ảnh tạm
        tmp_path = default_storage.save(f"tmp/{upload_image.name}", upload_image)
        full_path = default_storage.path(tmp_path)

        # Detect category từ YOLO
        detected_categories = detect_category(full_path)

        if not detected_categories:
            products = []
        else:
            #  Extract feature ảnh query
            query_feature = extract_feature(full_path)

            best_scores = {}

            # Lấy tất cả ảnh sản phẩm có feature
            product_images = (
                ProductImage.objects
                .filter(
                    product__status=True,
                    product__category__name__in=detected_categories,
                    image_feature__isnull=False
                )
                .select_related("product")
            )

            for img in product_images:
                try:
                    product_feature = pickle.loads(img.image_feature)
                    score = calc_similarity(query_feature, product_feature)

                    pid = img.product.id
                    if pid not in best_scores or score > best_scores[pid]["score"]:
                        best_scores[pid] = {
                            "product": img.product,
                            "score": score
                        }
                except Exception:
                    continue

            products = [
                v["product"]
                for v in sorted(
                    best_scores.values(),
                    key=lambda x: x["score"],
                    reverse=True
                )[:5]
            ]


    elif keyword:
        products = products_qs.filter(
            Q(name__icontains=keyword) |
            Q(brand__icontains=keyword) |
            Q(model__icontains=keyword)
        )


    else:
        products = products_qs

    if isinstance(products, list):
        pageObj = products
    else:
        paginator = Paginator(products, 10)
        page_number = request.GET.get("page")
        pageObj = paginator.get_page(page_number)


    discount_map = {}

    for p in pageObj:
        price, rule, orig = PromotionEngine.calculate_best_price(p)
        if rule:
            class DiscountObj:
                def __init__(self, p, pr, o):
                    self.product_id = p.id
                    self.discounted_price = pr
                    self.original_price = o

                def formatted_priceD(self):
                    return f"{int(self.discounted_price):,} VNĐ".replace(",", ".")

                def formatted_price(self):
                    return f"{int(self.original_price):,} VNĐ".replace(",", ".")

            discount_map[p.id] = DiscountObj(p, price, orig)

    return render(request, "products/product.html", {
        "products": pageObj,
        "pageObj": pageObj,
        "keyword": keyword,
        "discount_map": discount_map,
        "images": images,
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


