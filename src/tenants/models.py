from django.db import models
from django.conf import settings
from django.utils import timezone
from .utils import generate_schema_name
from helpers.db.validators import validate_blocked_subdomains,validate_subdomain
from django.core.management import call_command
import uuid
from .tasks import migrate_single_tenant_task
User=settings.AUTH_USER_MODEL
# Create your models here.
class Tenants(models.Model):
    id = models.UUIDField(default=uuid.uuid4,primary_key=True,db_index=True,editable=False)
    owner=models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    subdomain=models.CharField(max_length=60,db_index=True,unique=True,validators=[validate_subdomain,validate_blocked_subdomains])
    schema_name=models.CharField(max_length=60,db_index=True,unique=True,blank=True,null=True)
    active=models.BooleanField(default=True)
    active_at=models.DateTimeField(null=True,blank=True)
    inactive_at=models.DateTimeField(null=True,blank=True)
    timestamp=models.DateTimeField(auto_now_add=True)
    updated=models.DateTimeField(auto_now=True)

    def save(self,*args,**kwargs):
        now=timezone.now()
        if self.active and not self.active_at:
            self.active_at=now
            self.inactive_at=None
        elif not self.active and not self.inactive_at:
            self.inactive_at=now
            self.active_at=None
        if not self.schema_name:
            self.schema_name=generate_schema_name(self.id)
        super().save(*args,**kwargs)
        migrate_single_tenant_task(self.id)