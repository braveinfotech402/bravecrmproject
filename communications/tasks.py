from celery import shared_task
from django.core.mail import EmailMessage
import os
from django_tenants.utils import schema_context

from .models import Operator
from myapp.models import CustomUser
from firebase_admin import messaging, credentials
from firebase_admin.messaging import Message, Notification,send
from django.contrib.auth import get_user_model
from client_app.models import Lead
User = get_user_model()
from .firebase_util import send_fcm_notification


@shared_task
def send_call_request_fcm(data):
    user_id = data.get('user_id')
    phone = data.get('phone')
    schema_name = data.get('schema')

    print(f"Sending call request: user_id={user_id}, phone={phone}, schema={schema_name}")

    with schema_context(schema_name):
        try:
            user = User.objects.get(id=user_id)

            token = None

            if hasattr(user, 'staff') and user.staff.fcm_token:
                token = user.staff.fcm_token
                print("🔹 Token from Staff")
            elif hasattr(user, 'client') and user.client.fcm_token:
                token = user.client.fcm_token
                print("🔹 Token from Client")
            else:
                print(f"❌ No FCM token found for user_id={user_id}")
                return

            print(f"✅ FCM Token: {token}")
            print(f"📞 Push call request to {phone} using FCM...")

            success = send_fcm_notification(token, phone)
            if success:
                print("✅ Call request notification sent successfully")
            else:
                print("❌ Failed to send call request notification")

        except User.DoesNotExist:
            print(f"❌ User with id {user_id} not found.")
@shared_task
def send_email_to_lead(subject, message, to, cc=None, bcc=None, attachment_path=None):
    email = EmailMessage(
        subject=subject,
        body=message,
        to=to,
        cc=cc or [],
        bcc=bcc or [],
    )
    email.content_subtype = "html"

    if attachment_path and os.path.exists(attachment_path):
        email.attach_file(attachment_path)

    email.send()

    # Clean up file
    if attachment_path and os.path.exists(attachment_path):
        os.remove(attachment_path)
