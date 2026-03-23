from django.core.management import call_command
from helpers.db.schemas import use_tenant_schema
from django.db import connection

def migrate_single_tenant_task(tenant_id: str):
    from django.apps import apps
    Tenants = apps.get_model('tenants', 'Tenants')
    instance = Tenants.objects.get(id=tenant_id)
    schema_name = instance.schema_name

    try:
        with use_tenant_schema(schema_name=schema_name, create_if_missing=True):
            print(f"--- Running FULL Migration for schema: {schema_name} ---")
            
            # RUN ALL MIGRATIONS IN ONE SHOT
            # This is 10x faster and uses less RAM than looping through apps
            call_command("migrate", interactive=False, verbosity=1)
            
            print(f"--- Successfully finished {schema_name} ---")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error during migration: {e}")
    finally:
        # Crucial: Clean up connection to avoid "another command in progress" errors
        connection.close() 