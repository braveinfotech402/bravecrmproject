from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.core.paginator import Paginator
from client_app.models import Client,Lead
from client_app.models import Staff
from django.contrib import messages
from django.db.models import Q

# Create your views here.
@login_required
def staff_home(request):
    return render(request, 'staff_home.html')

from django.db.models import Q

@login_required
def staff_dashboard(request):
  if not hasattr(request.user, 'staff'):
        return redirect('login')

  client = request.user.staff.client
  leads = Lead.objects.filter(client=client)
  return render(request, 'staff_dashboard.html', {'leads': leads})

@login_required
def staff_create_lead(request):
    try:
        staff = Staff.objects.get(user=request.user)
        client = staff.client
    except Staff.DoesNotExist:
        return HttpResponseForbidden("Not authorized")

    if request.method == "POST":
        image = request.FILES.get('image')
        Lead.objects.create(
            firstname=request.POST.get('fname', '').strip(),
            lastname=request.POST.get('lname', '').strip(),
            streetaddress=request.POST.get('streetaddress', '').strip(),
            streetnumber=request.POST.get('streetnumber', '').strip(),
            postalcode=request.POST.get('postalcode', '').strip(),
            city=request.POST.get('city', '').strip(),
            state=request.POST.get('state', '').strip(),
            country=request.POST.get('country', '').strip(),
            phone=request.POST.get('phone', '').strip(),
            companyname=request.POST.get('companyname', '').strip(),
            tax=request.POST.get('tax', '').strip(),
            email=request.POST.get("email", '').strip(),
            status=request.POST.get("status", "new"),
            client=client,
            image=image
        )
        messages.success(request, "Lead created successfully!")
        return redirect("staff_dashboard")

    return render(request, "createlead.html")  # Reuse same template

@login_required
def lead_update(request, lead_id):
    lead = get_object_or_404(Lead, id=lead_id)
    
    # Client or staff check
    if request.user == lead.client.user:
        authorized = True
    else:
        try:
            staff = Staff.objects.get(user=request.user)
            authorized = staff.client == lead.client
        except Staff.DoesNotExist:
            authorized = False

    if not authorized:
        return HttpResponseForbidden("Not authorized")

    if request.method == "POST":
        for field in ['firstname', 'lastname', 'streetaddress', 'streetnumber', 'postalcode', 'city',
                      'state', 'country', 'phone', 'companyname', 'tax', 'email', 'status']:
            setattr(lead, field, request.POST.get(field, getattr(lead, field)))
        if 'image' in request.FILES:
            lead.image = request.FILES['image']
        lead.save()
        return redirect('client_dashboard' if request.user == lead.client.user else 'staff_dashboard')

    return render(request, 'lead_update.html', {'lead': lead})

@login_required
def lead_delete(request, lead_id):
    lead = get_object_or_404(Lead, id=lead_id)

    if request.user == lead.client.user:
        authorized = True
    else:
        try:
            staff = Staff.objects.get(user=request.user)
            authorized = staff.client == lead.client
        except Staff.DoesNotExist:
            authorized = False

    if not authorized:
        return HttpResponseForbidden("Not authorized")

    if request.method == "POST":
        lead.delete()
        return redirect('client_dashboard' if request.user == lead.client.user else 'staff_dashboard')

    return render(request, 'lead_confirm_delete.html', {'lead': lead})

@login_required
def staff_kanban_view(request):
    statuses = [
        ('new', 'New'),
        ('followup', 'Follow Up'),
        ('won', 'Won'),
        ('lost', 'Lost'),
        ('later', 'Later')
    ]

    leads = None

    if hasattr(request.user, 'client'):
        # Logged in as client
        leads = Lead.objects.filter(client__user=request.user)
    
    else:
        # Logged in as staff
        staff = Staff.objects.filter(user=request.user).first()

        if staff and staff.client:
            leads = Lead.objects.filter(client=staff.client)
        else:
            return HttpResponseForbidden("You are not authorized to view this page.")

    return render(request, 'kanban_view.html', {
        'leads': leads,
        'statuses': statuses
    })

    
@login_required
def update_lead_status(request):
    if request.method == 'POST':
        lead_id = request.POST.get('lead_id')
        new_status = request.POST.get('status')
        lead = get_object_or_404(Lead, id=lead_id)

        if request.user == lead.client.user:
            authorized = True
        else:
            try:
                staff = Staff.objects.get(user=request.user)
                authorized = staff.client == lead.client
            except Staff.DoesNotExist:
                authorized = False

        if not authorized:
            return JsonResponse({'error': 'Unauthorized'}, status=403)

        lead.status = new_status
        lead.save()
        return JsonResponse({'success': True})

    return JsonResponse({'error': 'Invalid request'}, status=400)