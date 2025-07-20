from django.db import models
from client_app.models import Lead
# Create your models here.
# models.py

class ActivityEntry(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE)
    note = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('myapp.CustomUser', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.timestamp} - {self.note[:30]}"
