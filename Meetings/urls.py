from django.urls import path
from . import views

urlpatterns = [
    path('meetings/', views.meeting_list, name='meeting_list'),
    path('meetings/create/', views.create_meeting, name='create_meeting'),
]
