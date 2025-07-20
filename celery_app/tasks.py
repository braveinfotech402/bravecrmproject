from celery import shared_task
from django.core.mail import send_mail
from django_tenants.utils import schema_context


@shared_task
def send_lead_status_email(tenant_schema_name, lead_id):
    from client_app.models import Lead
    """
    This task sends an email when a lead status changes (e.g., to 'Won' or 'Lost').
    It works within the tenant's schema context.
    """
    with schema_context(tenant_schema_name):
        try:
            lead = Lead.objects.get(id=lead_id)

            subject = f"Lead Status Update - {lead.status}"
            message = f"The lead '{lead.firstname} {lead.lastname}' has changed status to: {lead.status}"
            recipient_email = lead.client.user.email  # assuming OneToOne link to CustomUser

            send_mail(
                subject,
                message,
                'athiravs202@gmail.com',
                [recipient_email],
                fail_silently=False,
            )
            return f"Email sent to {recipient_email}"
        except Lead.DoesNotExist:
            return f"Lead with ID {lead_id} not found in schema '{tenant_schema_name}'"
        except Exception as e:
            return str(e)
