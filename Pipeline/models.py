from django.db import models
from django.contrib.auth import get_user_model
from client_app.models import Client,Column,Tag


class Pipeline(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True)

    column = models.ForeignKey(
        Column,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pipeline_leads'  # 🔁 renamed from 'cards'
    )
    title = models.CharField(max_length=255)
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    streetaddress = models.CharField(max_length=255, blank=True)
    streetnumber = models.CharField(max_length=50, blank=True)
    postalcode = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    companyname = models.CharField(max_length=255, blank=True)
    tax = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    image = models.ImageField(upload_to='lead_images/', null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)  # Assuming a Tag model
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.firstname} {self.lastname}"
    

