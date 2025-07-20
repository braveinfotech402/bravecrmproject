# client_app/urls.py

from django.urls import path
from . import views
app_name = 'Description'

urlpatterns = [
    
    
    path('<int:lead_id>/add_activity/', views.add_activity, name='add_activity'),

    path('<int:lead_id>/get_activities/', views.get_activities, name='get_activities'),
    
    path('<int:activity_id>/edit_activity/', views.edit_activity, name='edit_activity'),
    path('<int:activity_id>/delete_activity/', views.delete_activity, name='delete_activity'),

    
   
]
