from django.core.management import call_command
from django.apps import apps
from helpers.db.schemas import use_tenant_schema
from django.db import transaction

def migrate_single_tenant_task(tenant_id: str):
    Tenants = apps.get_model('tenants', 'Tenants')
    instance = Tenants.objects.get(id=tenant_id)
    schema_name = instance.schema_name

    # We use a nested atomic block to catch errors before they ruin the transaction
    with use_tenant_schema(schema_name=schema_name, create_if_missing=True, revert_public=True):
        print(f"--- Running Tenant Migration for: {schema_name} ---")
        
        # In multi-tenancy, it is safer to just run a full migrate
        # because the Router (Step 1) will now correctly handle what goes where
        try:
            # We call the full migrate, the router will filter 'accounts' automatically
            call_command("migrate", interactive=False, verbosity=1)
            print(f"Successfully migrated schema: {schema_name}")
        except Exception as e:
            print(f"ERROR during migration of {schema_name}: {e}")
            raise e