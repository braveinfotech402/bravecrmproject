# estimates/models.py

from django.db import models
from client_app.models import Lead, Client, Staff

class Estimate(models.Model):
    ESTIMATE_STATUS = (
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('expired', 'Expired'),
    )

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='estimates')
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='estimates')
    created_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True)
    estimate_number = models.CharField(max_length=50)
    customer_ref = models.CharField(max_length=255, blank=True)
    issue_date = models.DateField()
    expiry_date = models.DateField()
    status = models.CharField(max_length=20, choices=ESTIMATE_STATUS, default='draft')
    notes = models.TextField(blank=True)

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Estimate {self.estimate_number}"
    class Meta:
        unique_together = ('lead', 'estimate_number')
    
class EstimateItem(models.Model):
    estimate = models.ForeignKey(Estimate, on_delete=models.CASCADE, related_name='items')
    product_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product_name} ({self.quantity} x {self.price})"
