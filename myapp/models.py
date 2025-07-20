from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
import random
from django_tenants.models import TenantMixin, DomainMixin



class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser,PermissionsMixin):
    username = None  # Remove username field completely
    email = models.EmailField(unique=True, max_length=255)
    firstname=models.CharField(max_length=255,null=True, blank=True)
    lastname=models.CharField(max_length=255,null=True, blank=True)
    streetaddress=models.CharField(max_length=255,null=True, blank=True)
    streetnumber=models.CharField(max_length=255,null=True, blank=True)#
    postalcode=models.CharField(max_length=225,null=True, blank=True)
    city=models.CharField(max_length=255,null=True, blank=True)#
    state=models.CharField(max_length=255,null=True)
    country=models.CharField(max_length=255,null=True)#
    phone=models.CharField(max_length=255,null=True, blank=True)
    companyname=models.CharField(max_length=255,null=True, blank=True)#
    tax=models.CharField(max_length=255,null=True, blank=True)

    # Role-based fields
    is_superadmin = models.BooleanField(default=False)  # Full access, can manage tenants
    is_reseller = models.BooleanField(default=False)    # Manages multiple clients
    is_client = models.BooleanField(default=False)       # Owns leads and staff
    is_staff_user = models.BooleanField(default=False)   # Staff under a client
    is_lead = models.BooleanField(default=False)         # New field for leads

    # Profile & verification
    is_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    profile_image = models.ImageField(upload_to='images/', null=True, blank=True)
    
  

    # Required fields for AbstractUser
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # Required for Django Admin
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def generate_verification_code(self):
        self.verification_code = str(random.randint(100000, 999999))
        self.save()
        
class Reseller(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="reseller_profile")
    company_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    address = models.TextField()

    def __str__(self):
        return self.company_name

class Client(TenantMixin):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, max_length=255, null=True)
    image = models.ImageField(upload_to='images/')
    paid_until = models.DateField(null=True, blank=True)
    on_trial = models.BooleanField(default=True)
    created_on = models.DateTimeField(default=timezone.now)
    fcm_token = models.CharField(max_length=255, null=True, blank=True)
    # 👇 Required for django-tenants
    schema_name = models.CharField(max_length=63, unique=True, default='public')

    auto_create_schema = True

    def __str__(self):
        return self.name
class Domain(DomainMixin):
    tenant = models.ForeignKey(Client, related_name='domains', on_delete=models.CASCADE)
    is_primary = models.BooleanField(default=True)
    
    def __str__(self):
        return self.domain