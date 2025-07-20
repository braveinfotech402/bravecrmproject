from django.urls import path
from . import views

urlpatterns = [
    # urls.py
    path('create-lead/',views.create_lead, name='create_lead'),


    #path('board/<int:board_id>/', views.board_details, name='board_details'),  # Assuming you have this view for your board details page
]
