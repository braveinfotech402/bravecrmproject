# invoices/models.py

from django.db import models
from client_app.models import Lead, Client, Staff

class Invoice(models.Model):
    INVOICE_STATUS = (
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
    )

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='invoices')
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='invoices')
    created_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True)
    invoice_number = models.CharField(max_length=50)
    customer_ref = models.CharField(max_length=255, blank=True)
    issue_date = models.DateField()
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=INVOICE_STATUS, default='unpaid')
    notes = models.TextField(blank=True)

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('lead', 'invoice_number')

    def __str__(self):
        return f"Invoice {self.invoice_number}"


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    product_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product_name} ({self.quantity} x {self.price})"
