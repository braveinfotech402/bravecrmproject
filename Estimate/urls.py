# estimates/urls.py

from django.urls import path
from . import views

urlpatterns = [
   
   #path('create-estimate/', views.create_estimate_ajax, name='create_estimate_ajax'),
   path('api/next-estimate-number/',views.generate_estimate_number, name='next_estimate_number'),
   
   #path('preview-estimate-pdf/',views.preview_estimate_pdf, name='preview_estimate_pdf'),
   
   
   path('create-estimate/',views.create_estimate_ajax, name='create-estimate'),

   
   path('api/estimates/lead/<int:lead_id>/', views.get_estimates_by_lead, name='get_estimates_by_lead'),
   
   path('api/estimates/<int:estimate_id>/', views.estimate_detail_view),
   
   path('api/estimates/<int:estimate_id>/convert-to-invoice/', views.convert_estimate_to_invoice, name='convert_estimate_to_invoice'),
   
   path('estimates/', views.estimate_list, name='estimates'),
   
   path('get_lead_details/<int:lead_id>/', views.get_lead_details, name='get_lead_details'),



   
   



]
