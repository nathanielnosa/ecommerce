from distutils.sysconfig import customize_compiler
from django.contrib import admin

# Register your models here.
from . models import Customer

admin.site.register(Customer)