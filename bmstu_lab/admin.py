from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Users)
admin.site.register(Products)
admin.site.register(Application)
admin.site.register(ApplicationProducts)
