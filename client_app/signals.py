from django.db.models.signals import post_save
from django.dispatch import receiver
from client_app.models import Lead
from celery_app.tasks import send_lead_status_email
from django_tenants.utils import get_tenant_model

@receiver(post_save, sender=Lead)
def lead_status_change_handler(sender, instance, created, **kwargs):
    if not created and instance.status in ['Won', 'Lost']:
        # Get current schema (from related client)
        tenant = instance.client  # assuming Lead has FK to Client
        schema_name = tenant.schema_name

        send_lead_status_email.delay(schema_name, instance.id)
