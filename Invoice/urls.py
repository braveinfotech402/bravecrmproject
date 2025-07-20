# invoice/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('create-invoice/',views.create_invoice, name='create_invoice'),
    path('api/next-invoice-number/',views.generate_next_invoice_number, name='next_invoice_number'),
    path('api/invoices/lead/<int:lead_id>/', views.get_invoices_by_lead, name='get_invoices_by_lead'),
    path('api/products/',views.get_products_by_type, name='get_products_by_type'),
    path('api/invoices/<int:invoice_id>/', views.invoice_detail, name='invoice_detail'),
    path('invoice_list', views.invoice_list, name='invoice_list'),
    
    

]
