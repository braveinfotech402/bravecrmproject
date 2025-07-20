from django.db import models
from client_app.models import Lead  # Make sure this path is correct

class Proposal(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='proposals')
    to_email = models.EmailField(blank=True, null=True)
    subject = models.CharField(max_length=255, blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    attachment = models.FileField(upload_to='images', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Proposal to {self.to_email or 'N/A'}"
