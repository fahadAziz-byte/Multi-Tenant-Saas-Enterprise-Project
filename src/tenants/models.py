from django.db import models
from django.conf import settings
from django.utils import timezone
from .utils import generate_schema_name
from helpers.db.validators import validate_blocked_subdomains,validate_subdomain
from django.core.management import call_command
import threading
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
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

    def save(self, *args, **kwargs):
        # We ONLY handle the data logic here, NO migrations
        if not self.schema_name:
            from .utils import generate_schema_name
            self.schema_name = generate_schema_name(self.id)
        super().save(*args, **kwargs)

@receiver(post_save, sender=Tenants)
def trigger_tenant_migration(sender, instance, created, **kwargs):
    if created:
        from .tasks import migrate_single_tenant_task
        
        # We define a function to run the task
        def run_task():
            # Important: Close the connection in the new thread to get a fresh one
            from django.db import connection
            connection.close()
            migrate_single_tenant_task(instance.id)

        # We start the task in a separate Thread so the signup finishes immediately
        # transaction.on_commit ensures the thread starts only after the signup is saved
        transaction.on_commit(lambda: threading.Thread(target=run_task).start())