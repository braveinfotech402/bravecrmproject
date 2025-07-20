# accounts/views.py
from django.shortcuts import render, redirect
from.models import CustomUser,CustomUserManager
from client_app.models import Staff
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth.models import Group,Permission
from django.http import HttpResponse
from django.contrib.auth import authenticate,login
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.password_validation import validate_password
import datetime
from django_tenants.utils import schema_context
from django.utils.text import slugify
from myapp.models import Client, Domain
from django.utils import timezone
from django.core.management import call_command
from django_tenants.utils import schema_context, get_tenant_model, get_public_schema_name
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from myapp.tasks import send_welcome_email

def test_email(request):
    send_welcome_email.delay('recipient@example.com')
    return HttpResponse("Email task sent!")
#REGISTER VIEW
User = get_user_model()
Client = get_tenant_model()


def register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
       
        schema_name = request.POST.get('schema_name').lower()
        domain_name = request.POST.get('domain')

        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        streetaddress = request.POST.get('streetaddress')
        streetnumber = request.POST.get('streetnumber')
        postalcode = request.POST.get('postalcode')
        city = request.POST.get('city')
        state = request.POST.get('state')
        country = request.POST.get('country')
        phone = request.POST.get('phone')
        companyname=request.POST.get('companyname')
        tax = request.POST.get('tax')

        # Check uniqueness in public schema
        with schema_context('public'):
            if CustomUser.objects.filter(email=email).exists():
                messages.error(request, "User with this email already exists.")
                return redirect('register')

            if Client.objects.filter(schema_name=schema_name).exists():
                messages.error(request, "Schema already exists.")
                return redirect('register')

            if Domain.objects.filter(domain=domain_name).exists():
                messages.error(request, "Domain already exists.")
                return redirect('register')

            # Create user with additional details
            user = CustomUser.objects.create_user(
                email=email,
                password=password,
                
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
                is_client=True,
                is_verified=True
            )
            user.save()

            # Create tenant (Client)
            client = Client.objects.create(
                user=user,
                
                email=email,
                schema_name=schema_name,
                paid_until=timezone.now() + timezone.timedelta(days=30),
                on_trial=True
            )

            # Create domain for the tenant
            Domain.objects.create(
                domain=domain_name,
                tenant=client,
                is_primary=True
            )

        messages.success(request, "Tenant created successfully! Please login.")
        return redirect(f"http://{domain_name}/login/")

    return render(request, 'register.html')

def send_verification_email(user):
    subject = "Verify Your Email"
    message = f"Hello {user.email},\n\nYour verification code is: {user.verification_code}\n\nUse this code to verify your email."
    from_email = "athiravs202@gmail.com"
    recipient_list = [user.email]

    send_mail(subject, message, from_email, recipient_list)



def verify_email(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        code = request.POST.get('verifivation_code')

        try:
            user = CustomUser.objects.get(email=email)
            if user.verification_code == code:
                user.is_verified = True
                user.verification_code = ''
                user.save()
                messages.success(request, "Email verified! You can now log in.")
                return redirect('login')
            else:
                messages.error(request, "Invalid verification code.")
        except CustomUser.DoesNotExist:
            messages.error(request, "User not found.")
    
    return render(request, 'verify_email.html')


#CUSTOM LOGIN VIEW

def custom_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Authenticate with email and password
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)  # Ensure the user is logged in
            
            print(f"User logged in: {user}")  # Debugging line

            if hasattr(user, 'client'):
                return redirect('client_home')
            elif hasattr(user, 'staff_profile'):
                print("User has staff profile")
                return redirect('client_home')
            elif user.is_superuser:
                return redirect('superadmin_dashboard')
            else:
                return redirect('home')
        else:
            messages.error(request, "Invalid credentials")

    return render(request, 'account/login.html')
#SUPERADMIN CREATE GROUP

def createGroup(request):
    if request.method == 'POST':
        # Get the group name from the form
        group_name = request.POST.get('group_name')
        # Check if the group name is provided
        if group_name:
            # Create the group using Group.objects.create() (without get_or_create)
            try:
                group = Group.objects.create(name=group_name)
                message = f'Group "{group_name}" created successfully!'
            except Exception as e:
                message = f'An error occurred: {str(e)}'
        else:
            message = 'Please provide a valid group name.'
    else:
        message = None

    # Render the template with the message
    return render(request, 'createGroup.html', {'message': message})


#SUPERADMIN ASSIGN PERMISSION TO GROUP
def assignPermissionToGroup(request):
    if request.method == 'POST':
        # Retrieve the group name and permission codename from the form
        group_name = request.POST.get('group_name')
        permission_codename = request.POST.get('permission_codename')

        if group_name and permission_codename:
            try:
                # Retrieve the group by its name 
                group = Group.objects.get(name=group_name)

                # Retrieve the permission by its codename 
                permission = Permission.objects.get(codename=permission_codename)

                # Add the permission to the group
                group.permissions.add(permission)

                # Success message
                message = f'Permission "{permission_codename}" assigned to group "{group_name}" successfully!'
            except Group.DoesNotExist:
                message = f'Group "{group_name}" does not exist.'
            except Permission.DoesNotExist:
                message = f'Permission with codename "{permission_codename}" does not exist.'
            except Exception as e:
                message = f'An error occurred: {str(e)}'
        else:
            message = 'Please provide a valid group name and permission codename.'
    else:
        message = None

    return render(request, 'assignPermissionToGroup.html', {'message': message})


#SUPERADMIN ASSIGN USER TO GROUP
def assignUserToGroup(request):
    # Fetch all users and groups to display in the template
    users = CustomUser.objects.all()
    groups = Group.objects.all()

    if request.method == 'POST':
        # Get selected user and group from the form
        user_id = request.POST.get('user')
        group_id = request.POST.get('group')

        try:
            # Get the user and group by their IDs
            user = CustomUser.objects.get(id=user_id)
            group = Group.objects.get(id=group_id)

            # Assign the user to the group
            group.user_set.add(user)
            if group.name.lower() == 'staffs':
                if not Staff.objects.filter(user=user).exists():
                    if user.is_client:
                        client = user.client  # Assuming OneToOne relation exists
                        Staff.objects.create(user=user, client=client)
                    else:
                        # If user is not a client, you may handle this differently
                        return HttpResponse("Cannot assign a non-client user as staff.")

            # After assigning, redirect to a success page or back to the form
            return redirect('success')  # You can also render a success message here

        except (CustomUser.DoesNotExist, Group.DoesNotExist):
            # Handle invalid user/group selection if necessary
            return redirect('assignUserToGroup')  # Redirect to the same page on error
    
    # Render the page with users and groups
    return render(request, 'assignUserToGroup.html', {'users': users, 'groups': groups})


#SUPERADMIN SUCCESS VIEW
def success_view(request):
    return HttpResponse("""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Success</title>
        </head>
        <body>
            <h1>Success!</h1>
            <p>The user has been successfully assigned to the group.</p>
            <a href="{% url 'assignUserToGroup' %}">Go back to assign another user</a>
        </body>
        </html>
    """)
def form(request):
    return render(request,'form.html')
            

#HOME VIEW
#def home(request):
    return render(request,'home.html')
#SUPERADMIN DASHBOARD
def superadmin_dashboard(request):
    return render(request,'superadmin_dashboard.html')
#RESELLER DASHBOARD
def reseller_dashboard(request):
    return render(request,'reseller_dashboard.html')
#CLIENT DASHBOARD
#def client_dashboard(request):
    return render(request,'client_home.html')
#STAFF DASHBOARD
#def staff_dashboard(request):
    return render(request,'staff_dashboard.html')
#LEAD DASHBOARD
def leads_dashboard(request):
    return render(request,'leads_dashboard.html')



    
    