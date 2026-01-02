from django.urls import path
from .views import dashboard_day, dashboard_year, dashboard_event, dashboard_comment

urlpatterns = [
    path('', dashboard_day, name='dashboard_day'),
    path('year/', dashboard_year, name='dashboard_year'),
    path('event/', dashboard_event, name='dashboard_event'),
    path('comment/', dashboard_comment, name='dashboard_comment'),
]
