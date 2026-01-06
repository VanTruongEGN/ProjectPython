# scripts/db_utils.py
import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "TechStore.settings")
django.setup()

from products.models import Product

def get_products():
    return Product.objects.exclude(image='')

def update_feature(product_id, feature_bytes):
    Product.objects.filter(id=product_id).update(
        img_feature=feature_bytes
    )
