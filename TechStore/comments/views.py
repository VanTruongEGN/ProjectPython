import matplotlib.pyplot as plt
import io
import urllib, base64
from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from products.models import Product
from .models import  Comment
from django.db.models import Count

def review_chart(request, pk):
    product = get_object_or_404(Product, pk=pk, status=True)

    # Thống kê theo label
    review_counts = Comment.objects.filter(product=product).values('label').annotate(count=Count('id'))
    counts = {'tích cực': 0, 'trung lập': 0, 'tiêu cực': 0}
    for item in review_counts:
        counts[item['label']] = item['count']

    # Vẽ biểu đồ
    labels = ['Tích cực', 'Trung lập', 'Tiêu cực']
    values = [counts['tích cực'], counts['trung lập'], counts['tiêu cực']]
    colors = ['#4CAF50', '#C9CBCC', '#FF6384']

    plt.figure(figsize=(6,4))
    plt.bar(labels, values, color=colors)
    plt.title('Thống kê lượt đánh giá')
    plt.ylabel('Số lượt đánh giá')

    # Lưu ảnh vào buffer
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return HttpResponse(buf.getvalue(), content_type='image/png')