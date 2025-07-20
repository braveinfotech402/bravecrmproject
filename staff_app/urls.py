from django.urls import path, include
from .import views
from django.contrib.auth.views import LogoutView
from rest_framework.routers import DefaultRouter


urlpatterns = [
    
   
    path('staff_dashboard/',views.staff_dashboard, name='staff_dashboard'), 
    path('staff_home/', views.staff_home, name='staff_home'),
    path('kanban_view/',views.staff_kanban_view, name='staff_kanban_view'),
    
   
]