from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.html import strip_tags
from .models import Proposal, Lead  # Make sure these are imported

@csrf_exempt
def send_proposal(request):
    if request.method == 'POST':
        lead_id = request.POST.get('lead_id')
        to_email = request.POST.get('to_email', '')  # default to empty string
        subject = request.POST.get('subject', '')
        message = request.POST.get('message', '')
        file = request.FILES.get('file')

        try:
            lead = Lead.objects.get(id=lead_id)
        except Lead.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Lead not found'})

        # Save to DB even if fields are empty
        proposal = Proposal.objects.create(
            lead=lead,
            to_email=to_email,
            subject=subject,
            message=message,
            attachment=file
        )

        try:
            if to_email:
                email = EmailMessage(
                    subject=subject or "New Proposal",
                    body=strip_tags(message or "Please check attached proposal."),
                    from_email='athiravs202@email.com',
                    to=[to_email],
                )
                if file:
                    email.attach(file.name, file.read(), file.content_type)

                email.send()

            return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})
