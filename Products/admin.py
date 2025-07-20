from django.contrib import admin
from.models import *
# Register your models here.
admin.site.register(PhysicalCategory)
admin.site.register(DigitalCategory)
admin.site.register(CourseCategory)
admin.site.register(ServiceCategory)
admin.site.register(PhysicalProduct)
admin.site.register(DigitalProduct)
admin.site.register(Course)
admin.site.register(Service)