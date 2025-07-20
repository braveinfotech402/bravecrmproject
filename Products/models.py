from django.db import models

# Create your models here.


class PhysicalCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class DigitalCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class CourseCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class ServiceCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class PhysicalProduct(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='products/')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(PhysicalCategory, on_delete=models.SET_NULL, null=True, blank=True)

    description = models.TextField(blank=True)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return self.name

class DigitalProduct(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(DigitalCategory, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name

class Course(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='courses/', null=True, blank=True)
    category = models.ForeignKey(CourseCategory, on_delete=models.SET_NULL, null=True, blank=True)
    duration = models.CharField(max_length=100, blank=True)  # e.g., "6 weeks"
    fees = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.name

class Service(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(ServiceCategory, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name
