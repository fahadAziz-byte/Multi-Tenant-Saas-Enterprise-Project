from django.contrib import admin
from .models import Tenants
# Register your models here.
class TenantAdmin(admin.ModelAdmin):
    readonly_fields=["schema_name","active_at","inactive_at","timestamp","updated"]
    list_display=['subdomain','owner','schema_name']

admin.site.register(Tenants,TenantAdmin)
