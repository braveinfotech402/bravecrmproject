from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.mail import EmailMessage
from .tasks import send_email_to_lead
import traceback
import json
from .models import Operator
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from .models import QRToken, Operator
from client_app.models import Lead
from django_tenants.utils import get_tenant
import datetime, qrcode, io
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .tasks import send_call_request_fcm
from myapp.models import CustomUser
from django.db import connection
from firebase_admin import messaging
from client_app.models import Staff

@csrf_exempt
def send_call_fcm(request):
    try:
        data = json.loads(request.body)
        phone = data.get("phone")

        print("📞 Requested phone:", phone)

        if not phone:
            return JsonResponse({"error": "Phone number is required"}, status=400)

        lead = Lead.objects.filter(phone=phone).first()

        print("Lead Phone:", lead.phone)

        user = request.user
        client = user.client

        token = client.fcm_token
        if not token:
            return JsonResponse({"error": "No FCM token found"}, status=400)

        message = messaging.Message(
            notification=messaging.Notification(
                title="Make a Call",
                body=lead.phone,
            ),
            token=token,
        )
        response = messaging.send(message)
        print("✅ FCM sent:", response)
        return JsonResponse({"success": True})

    except Lead.DoesNotExist:
        return JsonResponse({"error": "Lead not found"}, status=404)
    except Exception as e:
        print("🔥 FCM send error:", e)
        return JsonResponse({"error": str(e)}, status=500) 




@login_required
def initiate_call(request, user_id):  # or just `request` if using request.user
    phone = request.GET.get("phone")
    schema_name = connection.schema_name

    send_call_request_fcm.delay({
    'user_id': user_id,
    'phone': phone,
    'schema': schema_name
})
    return JsonResponse({"status": "Call initiated"})
@csrf_exempt
def verify_qr_token(request):
    if request.method == "POST":
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        fcm_token = request.POST.get("fcm_token")
        try:
            qr = QRToken.objects.get(token=token, is_used=False)
            if (timezone.now() - qr.created_at) > datetime.timedelta(minutes=5):
                return JsonResponse({"error": "Token expired"}, status=403)
            qr.is_used = True
            qr.save()
            user = CustomUser.objects.get(user=qr.user)
            user.fcm_token = fcm_token
            user.save()
            return JsonResponse({"status": "verified"})
        except QRToken.DoesNotExist:
            return JsonResponse({"error": "Invalid token"}, status=400)

@csrf_exempt
def generate_qr(request, user_id):
    qr = QRToken.objects.create(operator_id=user_id)
    img = qrcode.make(qr.token)
    buf = io.BytesIO()
    img.save(buf)
    buf.seek(0)
    return HttpResponse(buf.getvalue(), content_type="image/png")




@csrf_exempt


def send_email_view(request):
    if request.method == "POST":
        try:
            to_email = request.POST.get("email")
            lead_name = request.POST.get("lead_name")
            subject = request.POST.get("subject")
            message = request.POST.get("message")
            cc = request.POST.get("cc")
            bcc = request.POST.get("bcc")

            attachment = request.FILES.get("attachment")

            email_msg = EmailMessage(
                subject=subject,
                body=message,
                from_email='braveinfomail@gmail.com',
                to=[to_email],
                cc=[cc] if cc else [],
                bcc=[bcc] if bcc else [],
            )

            if attachment:
                email_msg.attach(attachment.name, attachment.read(), attachment.content_type)

            email_msg.content_subtype = "html"
            print("📤 Sending to:", to_email)
            email_msg.send()  # Actually send
            print("✅ Sent!")

            return JsonResponse({"success": "Email sent!"})

        except Exception as e:
            print("❌ Error:", str(e))
            traceback.print_exc()
            return JsonResponse({"error": str(e)})