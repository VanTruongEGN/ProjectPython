# dashboard/views.py
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models.functions import TruncMonth, ExtractMonth, ExtractYear
from django.shortcuts import render
from django.db.models import Sum, Count
from django.utils import timezone
from orders.models import Order, OrderItem


def dashboard(request):
    today = timezone.now().date()

    # ===== FILTER INPUT =====
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    selected_year = request.GET.get('year', today.year)


    date_filter = {}

    if start_date:
        date_filter['order_date__date__gte'] = start_date
    if end_date:
        date_filter['order_date__date__lte'] = end_date
    orders = Order.objects.filter(status= 'Đã thanh toán',**date_filter)

    # ===== THỐNG KÊ TỔNG =====
    today_revenue = orders.filter(order_date__date=today) \
        .aggregate(total=Sum('total_amount'))['total'] or 0

    total_revenue = orders.filter(order_date__year=selected_year).aggregate(total=Sum('total_amount'))['total'] or 0

    total_orders = orders.filter(order_date__year=selected_year, **date_filter).count()

    # ===== DOANH THU THEO THÁNG (THEO NĂM CHỌN) =====
    revenue_by_month = (
        orders
        .filter(order_date__year=selected_year)
        .annotate(month=TruncMonth('order_date'))
        .values('month')
        .annotate(revenue=Sum('total_amount'))
        .order_by('month')
    )

    # ===== TOP SẢN PHẨM =====
    date_filter = {}
    if start_date:
        date_filter['order__order_date__gte'] = start_date
    if end_date:
        date_filter['order__order_date__lte'] = end_date
    top_products = (
        OrderItem.objects
        .filter(order__order_date__year=selected_year,order__status='Đã thanh toán',**date_filter)
        .values('product_id__id','product_id__name')
        .annotate(total_sold=Sum('quantity'))
        .order_by('-total_sold')[:5]
    )

    # ===== TOP KHÁCH HÀNG =====
    top_customers = (
        orders
        .values('customer__id','customer__full_name')
        .annotate(
            total_spent=Sum('total_amount'),
            total_orders=Count('id')
        )
        .order_by('-total_spent')[:5]
    )
    monthly_data = (
        orders
        .filter(order_date__year=selected_year)
        .annotate(month=ExtractMonth('order_date'))
        .values('month')
        .annotate(revenue=Sum('total_amount'))
    )

    # Map dữ liệu theo tháng
    revenue_map = {m['month']: m['revenue'] for m in monthly_data}

    month_labels = []
    month_values = []

    for m in range(1, 13):
        month_labels.append(f'Tháng {m}')
        month_values.append(float(revenue_map.get(m, 0)))

    year_list = (
        Order.objects
        .annotate(year=ExtractYear('order_date'))
        .values_list('year', flat=True)
        .distinct()
        .order_by('-year')
    )
    context = {
        'today_revenue': today_revenue,
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'month_labels': month_labels,
        'month_values': month_values,
        'top_products': top_products,
        'top_customers': top_customers,
        'year': int(selected_year),
        'start_date': start_date,
        'end_date': end_date,
        'year_list': year_list,
        'monthly_data':monthly_data,
        'revenue_map': revenue_map,
    }

    return render(request, 'admin/dashboard.html', context)
