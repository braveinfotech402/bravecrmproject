from django.urls import path
from .views import send_proposal

urlpatterns = [
    path('send-proposal/', send_proposal, name='send_proposal'),
]
