from django.core.management import call_command
from django.apps import apps
from helpers.db.schemas import use_tenant_schema

def migrate_single_tenant_task(tenant_id: str):
    Tenants = apps.get_model('tenants', 'Tenants')
    instance = Tenants.objects.get(id=tenant_id)
    schema_name = instance.schema_name

    # Switch context to the new tenant House
    with use_tenant_schema(schema_name=schema_name, create_if_missing=True, revert_public=True):
        print(f"--- Starting Migration for Tenant: {schema_name} ---")
        
        # We tell Django exactly which apps belong inside the house (Tenant)
        tenant_specific_apps = ['accounts', 'approvals', 'attendance']
        
        for app in tenant_specific_apps:
            print(f"Migrating app: {app}...")
            call_command("migrate", app, interactive=False, verbosity=1)

        print(f"--- Finished Setup for {schema_name} ---")