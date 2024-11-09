from django.contrib import admin
from .models import Manager

class ManagerAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_active')

admin.site.register(Manager, ManagerAdmin)
