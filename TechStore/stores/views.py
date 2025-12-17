# Create your views here.
# stores/views.py
from datetime import timezone

from django.db.models import Prefetch, Q
from django.shortcuts import render
from django.http import JsonResponse
from accounts.models import CartItem, Customer, Cart
from stores.models import Store, StoreInventory
from accounts.services import get_or_create_user_cart
from products.models import ProductDiscount, ProductImage, Category, ProductAttribute, Product


def home(request):
    images = ["store/images/img1.png", "store/images/img2.png", "store/images/img3.png"]
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
        'discount_by_category': discount_by_category,
        'images': images
    })

#accounts
def login_page(request):
    return render(request, 'accounts/login.html')

def register_page(request):
    return render(request, 'accounts/signup.html')

def personal_page(request):
    return render(request, 'accounts/profile.html')



def get_available_stores_for_cart(request):

    customer_id = request.session.get("customer_id")
    cart_items = []
    
    if customer_id:
        try:
            customer = Customer.objects.get(id=customer_id)
            cart = get_or_create_user_cart(customer)
            cart_items_qs = CartItem.objects.filter(cart=cart).select_related('product')
            for item in cart_items_qs:
                cart_items.append({
                    'product_id': item.product.id,
                    'quantity': item.quantity
                })
        except Customer.DoesNotExist:
            pass
    else:
        session_cart = request.session.get("cart", {})
        for pid, data in session_cart.items():
            cart_items.append({
                'product_id': pid,
                'quantity': int(data['qty'])
            })

    if not cart_items:
        return JsonResponse({'stores': []})
    valid_stores = []
    all_stores = Store.objects.all()

    for store in all_stores:
        is_valid = True
        for item in cart_items:
            product_id = item['product_id']
            qty = item['quantity']

            inventory = StoreInventory.objects.filter(
                store=store, 
                product_id=product_id
            ).first()
            
            if not inventory:
                is_valid = False
                break

            available = inventory.stock - inventory.reserved_stock
            if available < qty:
                is_valid = False
                break
        
        if is_valid:
            valid_stores.append({
                'id': store.id,
                'name': store.name,
                'address': f"{store.address_line}, {store.ward}, {store.district}, {store.city}"
            })

    return JsonResponse({'stores': valid_stores})

def search_product(request):
    keyword = request.GET.get("q", "").strip()

    products = Product.objects.filter(is_active=True)

    if keyword:
        products = products.filter(
            Q(name__icontains=keyword) |
            Q(description__icontains=keyword)
        )

    return render(request, "products/product.html", {
        "product": products,
        "keyword": keyword
    })