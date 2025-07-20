from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Lead,Staff,LeadColumn,NewBoard,Column,Card,Tag
from myapp.models import Client
from django.db import connection  # For tenant
from django.db.models import Q, Count
from django.http import HttpResponseForbidden, JsonResponse, HttpResponseNotAllowed
from django.contrib import messages
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.decorators.http import require_POST
import json
from bs4 import BeautifulSoup
from myapp.models import CustomUser
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import random
import string
from Description.models import ActivityEntry
from django.core.mail import send_mail
from .serializers import LeadSerializer
from django_tenants.utils import get_tenant
from django.utils import timezone
from django.db import transaction
from django_tenants.utils import get_tenant_model
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from django.conf import settings
from django.core.exceptions import PermissionDenied
import logging
from django.utils.text import slugify
from django.http import HttpResponse

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .serializers import LeadSerializer
from Products.models import PhysicalProduct,DigitalProduct,Course,Service
from Estimate.models import Estimate

@api_view(['GET', 'POST'])
def lead_list_create(request):
    if request.method == 'GET':
        leads = Lead.objects.all()
        serializer = LeadSerializer(leads, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = LeadSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def assign_user_to_tenant(user):
    Tenant = get_tenant_model()  # Get the tenant model
    User = get_user_model()  # Get the user model
    
    # Create a new tenant schema and user association
    tenant = Tenant.objects.create(schema_name=f"client{user.id}")
    user.client = tenant  # Assuming `user.client` refers to the tenant they belong to
    user.save()

    # Additional setup for user and tenant (such as role and permissions)
    return tenant
def home(request):
    context = {
        "new_leads_count": Lead.objects.filter(status="new").count(),
        "followup_leads_count": Lead.objects.filter(status="followup").count(),
        "won_leads_count": Lead.objects.filter(status="won").count(),
        "lost_leads_count": Lead.objects.filter(status="lost").count(),
        "later_leads_count": Lead.objects.filter(status="later").count(),
    }
    return render(request, "home.html", context)


@login_required
def client_home(request):
    return render(request, 'client_home.html', {'user': request.user})





class LeadViewSet(viewsets.ModelViewSet):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        lead = self.get_object()
        lead.status = request.data.get('status')
        lead.save()
        return Response({'status': 'updated'})


@login_required
def lead_detail(request, lead_id):
    lead = get_object_or_404(Lead, id=lead_id)

    # Check if client owns this lead
    if request.user == lead.client.user:
        return render(request, 'lead_detail.html', {'lead': lead})

    # Check if the user is staff of the lead's client
    if hasattr(request.user, 'staff_profile') and request.user.staff_profile.client == lead.client:
        return render(request, 'lead_detail.html', {'lead': lead})

    return HttpResponseForbidden("Not authorized")



@login_required
def createlead(request):
    # Identify the client (either directly or via staff)
    if hasattr(request.user, 'client'):
        client = request.user.client
    else:
        try:
            staff = Staff.objects.get(user=request.user)
            client = staff.client
        except Staff.DoesNotExist:
            return HttpResponseForbidden("You don't have an associated client or staff role.")

    if request.method == 'POST':
        # Get form data
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        streetaddress = request.POST.get('streetaddress')
        streetnumber = request.POST.get('streetnumber')
        postalcode = request.POST.get('postalcode')
        city = request.POST.get('city')
        state = request.POST.get('state')
        country = request.POST.get('country')
        phone = request.POST.get('phone')
        companyname = request.POST.get('companyname')
        tax = request.POST.get('tax')
        email = request.POST.get('email')
        status = request.POST.get('status', 'new')
        description = request.POST.get('description')
        image = request.FILES.get('image')

        # Create lead
        lead = Lead.objects.create(
            client=client,
            firstname=firstname,
            lastname=lastname,
            streetaddress=streetaddress,
            streetnumber=streetnumber,
            postalcode=postalcode,
            city=city,
            state=state,
            country=country,
            phone=phone,
            companyname=companyname,
            tax=tax,
            email=email,
            status=status,
            description=description,
            image=image,
        )

        # Handle tags
        tag_input = request.POST.get('tags', '')  # e.g. "tag1,tag2"
        tag_names = [t.strip() for t in tag_input.split(',') if t.strip()]
        for name in tag_names:
            tag_obj, created = Tag.objects.get_or_create(name=name, tenant=request.tenant)
            lead.tags.add(tag_obj)

        messages.success(request, "Lead created successfully!")

        return redirect('kanban_view')

    # GET request: render form with all available tags for Tagify whitelist
    tags = Tag.objects.filter(tenant=request.tenant)
    return render(request, 'createlead.html', {
        'tags': tags
    })

@login_required
def lead_update(request, lead_id):
    lead = get_object_or_404(Lead, id=lead_id)

    # Authorization
    if not (
        (hasattr(request.user, 'client') and request.user == lead.client.user) or
        (hasattr(request.user, 'staff_profile') and request.user.staff_profile.client == lead.client)
    ):
        return HttpResponseForbidden("Not authorized")

    if request.method == "POST":
        # Update fields
        for field in ['firstname', 'lastname', 'streetaddress', 'streetnumber', 'postalcode', 'city',
                      'state', 'country', 'phone', 'companyname', 'tax', 'email', 'status', 'description']:
            setattr(lead, field, request.POST.get(field, getattr(lead, field)))

        if 'image' in request.FILES:
            lead.image = request.FILES['image']

        lead.save()

        # Update tags
        tag_input = request.POST.get('tags', '')
        tag_names = [name.strip() for name in tag_input.split(',') if name.strip()]
        lead.tags.clear()
        for name in tag_names:
            tag_obj, _ = Tag.objects.get_or_create(name=name, tenant=request.tenant)
            lead.tags.add(tag_obj)

        messages.success(request, "Lead updated successfully!")
        return redirect('client_dashboard')

    # GET request
    current_tags = ','.join(tag.name for tag in lead.tags.all())
    all_tags = Tag.objects.filter(tenant=request.tenant)

    return render(request, 'lead_update.html', {
        'lead': lead,
        'current_tags': current_tags,
        'tags': all_tags
    })


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
        messages.success(request, "Lead deleted successfully.")
        return redirect('client_dashboard' if request.user == lead.client.user else 'staff_dashboard')

    return render(request, 'lead_confirm_delete.html', {'lead': lead})


def generate_password(length=8):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for i in range(length))
@login_required
def client_create_staff(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        whatsapp = request.POST.get('whatsapp')  # optional
        email = request.POST.get('email')
        password = get_random_string(length=8)  # Generate random password

        # Create user
        user = CustomUser.objects.create_user(
            email=email,
            password=password,
            is_active=True,
            is_verified=True,
        )

        # Create staff
        staff = Staff.objects.create(
            name=name,
            whatsapp=whatsapp,
            email=email,
            client=request.user.client,
            user=user,
            role='staff',
        )

        # Send email with password
        subject = "Welcome to CRM - Staff Login"
        message = f"""
Hello {name},

You have been added as a staff member to our CRM system.

Here are your login credentials:

📧 Email: {email}
🔐 Password: {password}

Login URL: http://your-tenant-url/login/

Please log in and change your password after your first login.

Best regards,  
CRM Team
"""
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

        # ← Add this:
        messages.success(
            request,
            f"Staff member {name!r} created successfully, and login credentials have been sent to {email}."
        )

        return redirect('staff_list')

    return render(request, 'client_create_staff.html')
@login_required
def client_dashboard(request):
    # Check if the user is either a Client or Staff
    if request.user.is_client:
        # Client: Show leads assigned to the client of the logged-in user
        leads = Lead.objects.filter(client__user=request.user).order_by('-created_by')
    elif request.user.is_staff_user:
        # Staff: Show leads associated with the client the staff is assigned to
        try:
            # Get the staff associated with the logged-in user (CustomUser)
            staff = Staff.objects.get(user=request.user)
            leads = Lead.objects.filter(client=staff.client)  # Leads assigned to the client of this staff
        except Staff.DoesNotExist:
            leads = Lead.objects.none()  # If staff is not assigned to a client, show no leads
    else:
        return HttpResponseForbidden("You are not allowed to access this page.")

    # Paginate leads
    paginator = Paginator(leads, 10)
    page_number = request.GET.get('page')
    return render(request, "client_dashboard.html", {"leads": paginator.get_page(page_number)})



@login_required
def profilesettings(request):
    return render(request, 'settings.html')


@login_required
def staff_list(request):
    user = request.user

    if user.is_client:
        client = user.client  # Assuming OneToOneField from CustomUser to Client
        staff_list = Staff.objects.filter(client=client)
    else:
        staff_list = []  # Optional: show nothing or redirect

    return render(request, 'staff_list.html', {'staff_list': staff_list})


@login_required
def user_profile(request):
    user = request.user

    if request.method == 'POST':
        user.firstname = request.POST.get('firstname', user.firstname)
        user.lastname = request.POST.get('lastname', user.lastname)
        user.streetaddress = request.POST.get('streetaddress', user.streetaddress)
        user.streetnumber = request.POST.get('streetnumber', user.streetnumber)
        user.postalcode = request.POST.get('postalcode', user.postalcode)
        user.city = request.POST.get('city', user.city)
        user.state = request.POST.get('state', user.state)
        user.country = request.POST.get('country', user.country)
        user.phone = request.POST.get('phone', user.phone)
        user.company = request.POST.get('company', user.company)
        user.tax = request.POST.get('tax', user.tax)

        # Avoid changing email unless explicitly needed
        new_email = request.POST.get('email')
        if new_email and new_email != user.email:
            if not CustomUser.objects.filter(email=new_email).exists():
                user.email = new_email
            else:
                messages.error(request, "This email is already in use.")
                return redirect('user_profile')

        # Handle image upload
        if 'profile_image' in request.FILES:
            user.profile_image = request.FILES['profile_image']

        user.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('user_profile')

    return render(request, 'profile.html', {'user': user})


@login_required
def edit_staff(request, staff_id):
    staff = get_object_or_404(Staff, id=staff_id)
    if request.method == "POST":
        staff.name = request.POST.get("name")
        staff.whatsapp = request.POST.get("whatsapp")
        staff.email = request.POST.get("email")
        staff.save()
        messages.success(request, "Staff updated successfully!")
        return redirect("profilesettings")
    return render(request, "edit_staff.html", {"staff": staff})


@login_required
def delete_staff(request, staff_id):
    staff = get_object_or_404(Staff, id=staff_id)
    if request.method == "POST":
        staff.delete()
        messages.success(request, "Staff deleted successfully!")
        return redirect("profilesettings")
    return render(request, "staff_list.html")


@login_required
def search(request):
    leads = Lead.objects.all()

    search_query = request.GET.get('search')
    status_filter = request.GET.get('status')

    if search_query:
        leads = leads.filter(
            Q(firstname__icontains=search_query) |
            Q(lastname__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(tags__name__icontains=search_query)  # if using taggit or similar
        ).distinct()

    if status_filter:
        leads = leads.filter(status=status_filter)

    context = {
        'leads': leads,
    }
    return render(request, 'client_dashboard.html', context)



def base(request):
    return render(request, 'base.html')

logger = logging.getLogger(__name__)

@login_required
def kanban_view(request):
    statuses = [
        ('new', 'New'),
        ('followup', 'Follow Up'),
        ('won', 'Won'),
        ('lost', 'Lost'),
        ('later', 'Later'),
    ]
    columns = LeadColumn.objects.all()
    leads = None
    estimates = None

    if hasattr(request.user, 'client'):
        # Client user - show only their leads
        leads = Lead.objects.filter(client__user=request.user)
        estimates = Estimate.objects.filter(client__user=request.user)

    elif hasattr(request.user, 'staff_profile'):
        staff = request.user.staff_profile
        if staff.client:
            leads = Lead.objects.filter(client=staff.client)
            estimates = Estimate.objects.filter(client=staff.client)
        else:
            return HttpResponseForbidden("You are not authorized to view this page.")
    
    else:
        return HttpResponseForbidden("You are not authorized to view this page.")

    return render(request, 'kanban_view.html', {
        'leads': leads,
        'statuses': statuses,
        'columns': columns,
        'estimates': estimates,  # ✅ Add this
    })



@csrf_exempt  # ONLY for testing, remove this later if you're using CSRF token
def create_custom_column(request):
    if request.method == 'POST':
        column_name = request.POST.get('column_name')
        color = request.POST.get('color', '#ffffff')

        if not column_name:
            return JsonResponse({'success': False, 'message': 'Column name is required.'})

        slug = slugify(column_name)
        if LeadColumn.objects.filter(slug=slug).exists():
            return JsonResponse({'success': False, 'message': 'Column with this name already exists.'})

        column = LeadColumn.objects.create(name=column_name, color=color, slug=slug)
        return JsonResponse({'success': True, 'message': f'Column "{column_name}" created successfully.', 'slug': slug})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})


#@login_required
#def get_lead(request, lead_id):
    #lead = get_object_or_404(Lead, id=lead_id)
    #return JsonResponse({
        #"firstname": lead.firstname,
        #"lastname": lead.lastname,
        #"streetaddress": lead.streetaddress,
        #"streetnumber": lead.streetnumber,
        #"postalcode": lead.postalcode,
        #"city": lead.city,
        #"state": lead.state,
        #"country": lead.country,
        #"phone": lead.phone,
        #"companyname": lead.companyname,
        #"tax": lead.tax,
        #"email": lead.email,
        #"status": lead.status
    #})

#logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)

@login_required
def get_lead(request, lead_id):
    lead = get_object_or_404(Lead, id=lead_id)
    return JsonResponse({
        "firstname": lead.firstname,
        "lastname": lead.lastname,
        "streetaddress": lead.streetaddress,
        "streetnumber": lead.streetnumber,
        "postalcode": lead.postalcode,
        "city": lead.city,
        "state": lead.state,
        "country": lead.country,
        "phone": lead.phone,
        "companyname": lead.companyname,
        "tax": lead.tax,
        "email": lead.email,
        "status": lead.status,
        "description": lead.description or "",  # 👈 Add this line
    })

@csrf_exempt
def update_lead_status(request, lead_id=None):
    if request.method == "POST":
        try:
            # Get data from JSON or form POST
            if request.content_type == "application/json":
                data = json.loads(request.body)
                status = data.get("status")
                lead_id = data.get("lead_id") or lead_id
            else:
                status = request.POST.get("status")
                lead_id = request.POST.get("lead_id") or lead_id

            if not status or not lead_id:
                return JsonResponse({"success": False, "error": "Missing status or lead_id"}, status=400)

            # Get the lead object from the current tenant schema
            lead = Lead.objects.get(id=lead_id)
            lead.status = status
            lead.save()

            return JsonResponse({"success": True, "message": "Lead status updated successfully."})
        except Lead.DoesNotExist:
            return JsonResponse({"success": False, "error": "Lead not found"}, status=404)
        except Exception as e:
            print("❌ Error updating lead status:", e)
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return JsonResponse({"success": False, "error": "Invalid request method"}, status=405)

@csrf_exempt
def update_lead(request, lead_id):
    if request.method == "POST":
        lead = get_object_or_404(Lead, id=lead_id)
        lead.description = request.POST.get("lead_details", "")
        lead.save()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False, "error": "Invalid request"})





@login_required
def client_won(request):
    clients = None

    # If logged in as a client
    if hasattr(request.user, 'client'):
        clients = Client.objects.filter(id=request.user.client.id) \
            .annotate(won_leads_count=Count('lead', filter=Q(lead__status='won'))) \
            .select_related('user') \
            .distinct()

    # If logged in as staff of a client
    elif hasattr(request.user, 'staff'):
        staff = Staff.objects.filter(user=request.user).first()
        if staff and staff.client:
            clients = Client.objects.filter(id=staff.client.id) \
                .annotate(won_leads_count=Count('lead', filter=Q(lead__status='won'))) \
                .select_related('user') \
                .distinct()

    else:
        # Optionally handle superadmin/reseller view if needed
        return render(request, '403.html', status=403)


    return render(request, 'client_won.html', {'clients': clients})
def send_email(request, lead_id):
    lead = get_object_or_404(Lead, id=lead_id)
    subject = f"Hello {lead.firstname}, here is your lead update"
    message = "This is a sample message content."
    from_email = 'athiravs292@gmail.com'  # Update this with the sender email

    # Send the email to the lead's email address
    send_mail(subject, message, from_email, [lead.email])

    # Return a JSON response with the lead's email
    return JsonResponse({'email': lead.email})

def tenant_home(request):
    return HttpResponse("Welcome to Tenant Site")

@login_required
def create_board(request):
    if request.method == 'POST':
        name = request.POST.get('board_name')
     # Default template if not selected

        if NewBoard.objects.filter(name=name).exists():
            messages.error(request, "A board with this name already exists.")
            return redirect('pipeline')  # Adjust as per your UI flow

        board = NewBoard.objects.create(
            name=name,
           # Save the selected template
            created_by=request.user
        )

        return redirect('board_details', board.id)

@login_required
def board_details(request, board_id):
    board = get_object_or_404(NewBoard, id=board_id)
    columns = board.columns.all()

    if request.method == "POST":
        if 'column_name' in request.POST:
            column_name = request.POST.get('column_name')
            if column_name:
                Column.objects.create(board=board, name=column_name)
                return redirect('board_details', board_id=board.id)
        elif 'title' in request.POST:
            column_id = request.POST.get('column_id')
            title = request.POST.get('title')
            if column_id and title:
                column = get_object_or_404(Column, id=column_id)
                Card.objects.create(column=column, title=title)
                return redirect('board_details', board_id=board.id)

    return render(request, 'board_details.html', {
        'board': board,
        'columns': columns
    })

def board_list(request):
    boards = NewBoard.objects.filter(created_by=request.user)
    return render(request, 'board_list.html', {'boards': boards})

@login_required
def create_column(request, board_id):
    board = get_object_or_404(NewBoard, id=board_id, created_by=request.user)
    if request.method == 'POST':
        name = request.POST.get('column_name')
        color = request.POST.get('color', '#ffffff')
        slug = slugify(name)
        order = board.columns.count()
        LeadColumn.objects.create(name=name, color=color, slug=slug, order=order, newboard=board)
        return redirect('board_details', board_id=board_id)
    
logger = logging.getLogger(__name__)

def pipeline(request):
    boards = NewBoard.objects.filter(created_by=request.user)  # List all boards created by this user
    return render(request, 'pipeline.html', {'boards': boards})


@csrf_exempt
@login_required
def ajax_add_column(request, board_id):
    if request.method == 'POST':
        board = get_object_or_404(NewBoard, id=board_id)
        data = json.loads(request.body)
        name = data.get('name')
        if name:
            column = Column.objects.create(board=board, name=name)
            return JsonResponse({
                'success': True,
                'column_id': column.id,
                'name': column.name,
                'color': column.color or '#f1f1f1'
            })
    return JsonResponse({'success': False})
@csrf_exempt
def add_card(request, column_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        title = data.get('title')
        column = Column.objects.get(id=column_id)
        card = Card.objects.create(column=column, title=title)
        return JsonResponse({'success': True, 'title': card.title})
    return JsonResponse({'success': False})

@csrf_exempt
def move_card(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        card_id = data.get('card_id')
        new_column_id = data.get('new_column_id')

        try:
            card = Card.objects.get(id=card_id)
            column = Column.objects.get(id=new_column_id)
            card.column = column
            card.save()
            return JsonResponse({'success': True})
        except (Card.DoesNotExist, Column.DoesNotExist):
            return JsonResponse({'success': False, 'error': 'Not found'})
    return JsonResponse({'success': False, 'error': 'Invalid method'})

def ajax_card_detail(request, card_id):
    # Fetch the card using the ID
    card = get_object_or_404(Card, id=card_id)
    
    # Return a rendered template with the card data as HTML
    return render(request, 'card_detail.html', {'card': card})

@csrf_exempt  # Remove if you have proper CSRF token handling
@require_POST
def update_lead_description(request, lead_id):
    try:
        print(f"Update request received for lead {lead_id}")
        data = json.loads(request.body)
        print(f"Data received: {data}")

        lead = Lead.objects.get(id=lead_id)
        lead.details = data.get('lead_details', '')
        lead.save()

        print("Lead updated successfully!")
        return JsonResponse({'success': True})
    except Lead.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Lead not found'})
    except Exception as e:
        print("Error updating lead:", e)
        return JsonResponse({'success': False, 'error': str(e)})



# views.py
from django.http import JsonResponse

def all_products_json(request):
    physicals = PhysicalProduct.objects.all()
    digitals = DigitalProduct.objects.all()
    courses = Course.objects.all()
    services = Service.objects.all()

    products = []

    for p in physicals:
        products.append({
            'id': p.id,
            'name': p.name,
            'type': 'physical',
            'price': float(p.price),
            'quantity': p.quantity,
            'image': p.image.url if p.image else '',
            'description': p.description,
            'category': p.category.id if p.category else '',
            'category_name': p.category.name if p.category else '',
        })

    for d in digitals:
        products.append({
            'id': d.id,
            'name': d.name,
            'type': 'digital',
            'price': float(d.price),
            'quantity': '',
            'image': d.image.url if d.image else '',
            'description': '',
            'category': d.category.id if d.category else '',
            'category_name': d.category.name if d.category else '',
        })

    for c in courses:
        products.append({
            'id': c.id,
            'name': c.name,
            'type': 'course',
            'price': float(c.fees),
            'quantity': '',
            'image': c.image.url if c.image else '',
            'description': c.description,
            'category': c.category.id if c.category else '',
            'category_name': c.category.name if c.category else '',
        })

    for s in services:
        products.append({
            'id': s.id,
            'name': s.name,
            'type': 'service',
            'price': 0,
            'quantity': '',
            'image': '',
            'description': '',
            'category': s.category.id if s.category else '',
            'category_name': s.category.name if s.category else '',
        })

    return JsonResponse({'products': products})




def get_lead_details(request, lead_id):
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])
    
    try:
        lead = Lead.objects.get(id=lead_id)
    except Lead.DoesNotExist:
        return JsonResponse({'error': 'Lead not found'}, status=404)
    
    data = {
        'firstname': lead.firstname or '',
        'lastname': lead.lastname or '',
        'streetaddress': lead.streetaddress or '',
        'streetnumber': lead.streetnumber or '',
        'postalcode': lead.postalcode or '',
        'city': lead.city or '',
        'state': lead.state or '',
        'country': lead.country or '',
        'phone': lead.phone or '',
        'companyname': lead.companyname or '',
        'tax': lead.tax or '',
        'email': lead.email or '',
        'status': lead.status or '',
        'description': lead.description or '',
        # You can add more fields as needed
    }
    
    return JsonResponse(data)



@csrf_exempt
def update_lead_fields(request, lead_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body)
        html_content = data.get('content', '')

        soup = BeautifulSoup(html_content, 'html.parser')

        def get_text(label):
            tag = soup.find(string=lambda text: label in text)
            if tag and tag.find_parent() and tag.find_parent().next_sibling:
                return tag.find_parent().next_sibling.get_text(strip=True)
            return ''

        name = get_text("Name:").split()
        firstname = name[0] if len(name) > 0 else ''
        lastname = ' '.join(name[1:]) if len(name) > 1 else ''

        email = soup.find('h2').get_text(strip=True) if soup.find('h2') else ''
        phone = get_text("Phone:")
        company = get_text("Company:")
        status = get_text("Status:")
        address = get_text("Address:")  # we'll split this
        address_parts = address.split(',')

        streetaddress = address_parts[0].strip() if len(address_parts) > 0 else ''
        city = address_parts[1].strip() if len(address_parts) > 1 else ''
        state = address_parts[2].strip() if len(address_parts) > 2 else ''
        country = address_parts[3].strip() if len(address_parts) > 3 else ''

        lead = Lead.objects.get(id=lead_id)
        lead.firstname = firstname
        lead.lastname = lastname
        lead.email = email
        lead.phone = phone
        lead.companyname = company
        lead.status = status
        lead.streetaddress = streetaddress
        lead.city = city
        lead.state = state
        lead.country = country
        lead.save()

        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


