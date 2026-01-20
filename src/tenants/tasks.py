from django.core.management import call_command
from helpers.db.schemas import use_tenant_schema
from django.conf import settings
from django.apps import apps
import logging

def migrate_single_tenant_task(tenant_id: str):
    Tenants = apps.get_model('tenants', 'Tenants')
    instance = Tenants.objects.get(id=tenant_id)
    schema_name = instance.schema_name

    with use_tenant_schema(schema_name=schema_name, create_if_missing=True):
        try:
            print(f"--- Starting Migrations for Tenant: {schema_name} ---")
            
            # Loop through only tenant-specific apps to ensure 
            # their tables (like Departments) are created in this schema
            for app in settings.CUSTOMER_INSTALLED_APPS:
                print(f"Applying migrations for app: {app}")
                call_command("migrate", app, interactive=False, verbosity=1)
            
            print(f"--- Successfully set up {schema_name} ---")
        except Exception as e:
            print(f"Error during tenant migration: {e}")