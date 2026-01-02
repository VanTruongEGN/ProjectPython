from django.contrib.admin.views.decorators import staff_member_required
from django.db.models.functions import TruncMonth, ExtractMonth, ExtractYear, datetime
from django.shortcuts import render
from django.db.models import Sum, Count
from django.utils import timezone

from comments.models import Comment
from orders.models import Order, OrderItem
from datetime import datetime, date

from django.db.models import Sum, F
from django.utils.timezone import now
from orders.models import Order, OrderItem
from products.models import Product
from promotions.models import PromotionEvent



@staff_member_required
def dashboard_day(request):
    today = timezone.now().date()

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if not start_date and not end_date:
        start_date = today
        end_date = today
    if not end_date:
        end_date = today

    date_filter = {}
    if start_date:
        date_filter['order_date__date__gte'] = start_date
    if end_date:
        date_filter['order_date__date__lte'] = end_date

    orders = Order.objects.filter(status='Đã thanh toán', **date_filter)

    daily_revenue = orders.aggregate(total=Sum('total_amount'))['total'] or 0
    daily_orders = orders.count()

    daily_top_customers = (
        orders.values('customer__id', 'customer__full_name')
        .annotate(total_spent=Sum('total_amount'), total_orders=Count('id'))
        .order_by('-total_spent')[:5]
    )

    daily_top_products = (
        OrderItem.objects.filter(order__in=orders)
        .values('product__id', 'product__name')
        .annotate(total_sold=Sum('quantity'))
        .order_by('-total_sold')[:5]
    )

    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    context = {
        'view_type': 'day',
        'daily_revenue': daily_revenue,
        'daily_orders': daily_orders,
        'daily_top_products': daily_top_products,
        'daily_top_customers': daily_top_customers,
        'start_date': start_date,
        'end_date': end_date,
    }

    return render(request, 'admin/dashboard.html', context)
def dashboard_year(request):
    today = timezone.now().date()
    selected_year = int(request.GET.get('year', today.year))

    yearly_orders = Order.objects.filter(
        status='Đã thanh toán',
        order_date__year=selected_year
    )

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
        'view_type': 'year',
        'year': selected_year,
        'year_list': year_list,
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'top_products': top_products,
        'top_customers': top_customers,
        'month_labels': month_labels,
        'month_values': month_values,
    }

    return render(request, 'admin/dashboard.html', context)
def dashboard_event(request):
    promotions = PromotionEvent.objects.all()
    selected_ids = request.GET.getlist('promotion_ids')

    event_stats = []
    event_labels = []
    event_values = []
    event_chart = False

    if selected_ids:
        event_chart = True
        events = PromotionEvent.objects.filter(id__in=selected_ids)

        for event in events:
            orders = Order.objects.filter(
                promotion=event,
                status='Đã thanh toán'
            )

            revenue = OrderItem.objects.filter(
                order__in=orders
            ).aggregate(
                total=Sum(F('unit_price') * F('quantity'))
            )['total'] or 0

            event_stats.append({
                'event': event,
                'total_orders': orders.count(),
                'revenue': revenue
            })

            event_labels.append(event.name)
            event_values.append(float(revenue))

    context = {
        'view_type': 'event',
        'promotions': promotions,
        'selected_promotion_ids': selected_ids,
        'event_stats': event_stats,
        'event_labels': event_labels,
        'event_values': event_values,
        'event_chart': event_chart,
    }

    return render(request, 'admin/dashboard.html', context)