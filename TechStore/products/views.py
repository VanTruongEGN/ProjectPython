import datetime

from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from accounts.models import Customer
from comments.models import Comment
from .models import Product, ProductDiscount, Category, ProductAttribute


def product_page(request,category_name):
    images = ["products/images/img1.png", "products/images/img2.png", "products/images/img3.png"]

    tablet_category = Category.objects.filter(name__iexact=category_name).first()

    products = Product.objects.filter(category=tablet_category, status=True)
    discounts = ProductDiscount.objects.all()
    discount_map = {d.product.id: d for d in discounts}

    return render(request, 'products/product.html', {
        'products': products,
        'discount_map': discount_map,
        'images': images,
    })

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, status=True)
    comment = Comment.objects.filter(product_id=pk).first()
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
        'discount': discount,
        'comment': comment,
    })
def addComment(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    customer_id = request.session.get("customer_id")
    if not customer_id:
        return JsonResponse({"error": "Bạn cần đăng nhập"}, status=401)

    content = request.POST.get("content")
    rating = request.POST.get("rating")
    product_id = request.POST.get("product_id")

    if not content or not product_id:
        return JsonResponse({"error": "Thiếu dữ liệu"}, status=400)

    customer = Customer.objects.get(id=customer_id)
    product = Product.objects.get(id=product_id)

    comment = Comment.objects.create(
        customer=customer,
        product=product,
        content=content,
        rating=rating
    )

    return JsonResponse({
        "success": True,
        "customer_name": customer.full_name,
        "content": comment.content,
        "rating": comment.rating,
        "created_at": datetime.now().strftime("%d/%m/%Y")
    })


