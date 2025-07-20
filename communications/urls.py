from django.urls import path
from . import views

urlpatterns = [
    
    
    path('send-email/',views.send_email_view, name='send_email_view'),
    path('initiate-call/<int:user_id>/', views.initiate_call, name='initiate_call'),
    path('api/verify-qr-token/', views.verify_qr_token),
    path('api/generate-qr/<int:user_id>/', views.generate_qr, name='generate_qr'),
    path('api/send-call/',views.send_call_fcm, name='send_call_fcm'),
 

]
