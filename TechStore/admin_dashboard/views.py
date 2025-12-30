from django.contrib.admin.views.decorators import staff_member_required
from django.db.models.functions import TruncMonth, ExtractMonth, ExtractYear
from django.shortcuts import render
from django.db.models import Sum, Count
from django.utils import timezone
from orders.models import Order, OrderItem


@staff_member_required
def dashboard(request):
    today = timezone.now().date()

    # ===== FILTER INPUT =====
    view_type = request.GET.get('view_type', 'day')  # 'day' hoặc 'year'
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    selected_year = int(request.GET.get('year', today.year))

    orders = Order.objects.filter(status='Đã thanh toán')
    if not start_date and not end_date:
        start_date = end_date = today
    date_filter = {}
    if start_date: date_filter['order_date__date__gte'] = start_date
    if end_date: date_filter['order_date__date__lte'] = end_date

    # ===== THỐNG KÊ THEO NGÀY =====
    ordersByDate = orders.filter(**date_filter)
    daily_revenue = ordersByDate.aggregate(total=Sum('total_amount'))['total'] or 0
    daily_orders = ordersByDate.count()

    daily_top_customers = (
        ordersByDate
        .values('customer__id', 'customer__full_name')
        .annotate(total_spent=Sum('total_amount'), total_orders=Count('id'))
        .order_by('-total_spent')[:5]
    )
    date_filter = {}
    if start_date: date_filter['order__order_date__gte'] = start_date
    if end_date: date_filter['order__order_date__lte'] = end_date


    daily_top_products = (
        OrderItem.objects.filter(order__in=ordersByDate)
        .values('product__id', 'product__name')
        .annotate(total_sold=Sum('quantity'))
        .order_by('-total_sold')[:5]
    )

    # ===== THỐNG KÊ THEO NĂM =====
    yearly_orders = Order.objects.filter(status='Đã thanh toán', order_date__year=selected_year)

    total_revenue = yearly_orders.aggregate(total=Sum('total_amount'))['total'] or 0
    total_orders = yearly_orders.count()

    top_products = (
        OrderItem.objects.filter(order__in=yearly_orders)
        .values('product__id', 'product__name')
        .annotate(total_sold=Sum('quantity'))
        .order_by('-total_sold')[:5]
    )

    top_customers = (
        yearly_orders.values('customer__id', 'customer__full_name')
        .annotate(total_spent=Sum('total_amount'), total_orders=Count('id'))
        .order_by('-total_spent')[:5]
    )

    monthly_data = (
        yearly_orders
        .annotate(month=ExtractMonth('order_date'))
        .values('month')
        .annotate(revenue=Sum('total_amount'))
    )

    revenue_map = {m['month']: m['revenue'] for m in monthly_data}

    month_labels = [f'Tháng {m}' for m in range(1, 13)]
    month_values = [float(revenue_map.get(m, 0)) for m in range(1, 13)]

    year_list = (
        Order.objects
        .annotate(year=ExtractYear('order_date'))
        .values_list('year', flat=True)
        .distinct()
        .order_by('-year')
    )

    context = {
        'view_type': view_type,
        'daily_revenue': daily_revenue,
        'daily_orders': daily_orders,
        'daily_top_products': daily_top_products,
        'daily_top_customers': daily_top_customers,
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'top_products': top_products,
        'top_customers': top_customers,
        'month_labels': month_labels,
        'month_values': month_values,
        'year': selected_year,
        'start_date': start_date,
        'end_date': end_date,
        'year_list': year_list,
    }

    return render(request, 'admin/dashboard.html', context)
