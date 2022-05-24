from django.urls import path
from . import views

urlpatterns = [
    path('report', views.create_report, name='report'),
    path('customer-report', views.create_customer_report, name='customer-report'),
    path('customer-report/<int:customer_id>', views.get_customer_report, name='customer-report-id')
]
