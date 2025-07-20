from django.db import models
from django.utils import timezone

from myapp.models import CustomUser
import uuid


    

class Operator(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    fcm_token = models.CharField(max_length=255)


class QRToken(models.Model):
    token = models.CharField(max_length=255, unique=True, default=uuid.uuid4)
    operator = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    is_used = models.BooleanField(default=False)