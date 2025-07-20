from django.db import models
from myapp.models import CustomUser
from django.conf import settings
from myapp.models import Client
from django.utils.text import slugify
from communications.models import Operator




# Create your models here.



from django.utils import timezone

class NewBoard(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="boards")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    template = models.CharField(max_length=100, default='blue')

    def __str__(self):
        return self.name

class LeadColumn(models.Model):
    
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=20, default='#ffffff')
    slug = models.SlugField(unique=True)
    order = models.PositiveIntegerField(default=0)  # Added for ordering
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['order']  
        
class Tag(models.Model):
    name = models.CharField(max_length=50)
    tenant = models.ForeignKey(Client, on_delete=models.CASCADE)  # Multi-tenant aware

    def __str__(self):
        return self.name
    
class Lead(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('followup', 'Follow up'),
        ('won', 'Won'),
        ('lost', 'Lost'),
        ('later', 'Later'),
    ]
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
    email = models.EmailField(unique=False, blank=True)
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default='new', blank=True)
    #user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,null=True)  # Link to the user
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True)
    created_by = models.ForeignKey('myapp.CustomUser', on_delete=models.SET_NULL, null=True, blank=True)
    custom_column = models.ForeignKey(LeadColumn, null=True, blank=True, on_delete=models.SET_NULL) 
    tags = models.ManyToManyField(Tag, blank=True)
    assigned_operator = models.ForeignKey(Operator, on_delete=models.SET_NULL, null=True)
    board_id = models.IntegerField(null=True, blank=True)
    column_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.firstname if self.firstname else "Unnamed Lead"   
    

  
    
class Staff(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    whatsapp = models.CharField(max_length=222, null=True, blank=True)
    email = models.EmailField(unique=True, max_length=255)
    client = models.ForeignKey(
        Client,
        related_name='staff_members',
        on_delete=models.CASCADE
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='staff_profile'   # <<< important
    )
    role = models.CharField(
        max_length=100,
        choices=[('client', 'client'), ('Staff', 'Staff')],
        default='Staff'
      
    )
    fcm_token = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.user.email} - {self.role}'
    

class Board(models.Model):
    name = models.CharField(max_length=100)
    template = models.CharField(max_length=50, default='default')  # e.g., 'dark', 'blue', etc.

    def __str__(self):
        return self.name

class Column(models.Model):
    board = models.ForeignKey(NewBoard, on_delete=models.CASCADE, related_name='columns')
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default='#ffffff')  # hex color

    def __str__(self):
        return self.name

class Card(models.Model):
    column = models.ForeignKey(Column, on_delete=models.CASCADE, related_name='cards')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True) 
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, null=True, blank=True)# optional: for future Trello-like details

    def __str__(self):
        return self.title
    
    

    



