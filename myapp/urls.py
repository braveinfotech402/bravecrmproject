from django.urls import path
from . import views
from .views import createGroup
from .views import assignPermissionToGroup
from.views import assignUserToGroup

    


urlpatterns = [
    #path('',views.home,name='home'),
    path('register/', views.register, name='register'),
    path('createGroup/', views.createGroup, name='createGroup'),
    path('assignPermissionToGroup/',views.assignPermissionToGroup, name='assignPermissionToGroup'),
    path('assignUserToGroup/', views.assignUserToGroup, name='assignUserToGroup'),
    path('success/', views.success_view, name='success'),
    path('custom_login/', views.custom_login, name='custom_login'), 
    path('verify-email/<str:email>/', views.verify_email, name='verify_email'),
    path('superadmin_dashboard/', views.superadmin_dashboard, name='superadmin_dashboard'),
    path('reseller_dashboard/', views.reseller_dashboard, name='reseller_dashboard'),
    #path('client_dashboard/', views.client_dashboard, name='client_dashboard'),
    #path('staff_dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('leads_dashboard/', views.leads_dashboard, name='leads_dashboard'),
    path('form/', views.form, name='form'),
    
    path('test-email/', views.test_email, name='test_email'),

    
    
    
]