from django.core.management import call_command
from helpers.db.schemas import use_tenant_schema
from helpers.db.statements import ACTIVATE_SCHEMA_SQL
from django.db import connection


def migrate_single_tenant_task(tenant_id: str):
    """
    Run ONLY tenant-app migrations inside a new tenant's schema.

    IMPORTANT: We only migrate TENANT_APPS here. Shared apps (auth, sessions, etc.)
    already live in the public schema and must NOT be duplicated into tenant schemas.
    Doing so is what caused the cross-tenant table fallback bug.
    """
    from django.apps import apps
    from cfehome.installed import TENANT_APPS

    Tenants = apps.get_model('tenants', 'Tenants')
    instance = Tenants.objects.get(id=tenant_id)
    schema_name = instance.schema_name

    print(f"[TENANT MIGRATION] Starting migration for schema: {schema_name}")
    print(f"[TENANT MIGRATION] Will migrate these apps: {TENANT_APPS}")

    try:
        with use_tenant_schema(schema_name=schema_name, create_if_missing=True):
            print(f"--- Running TENANT-ONLY Migration for schema: {schema_name} ---")

            # Verify search_path before migrating
            with connection.cursor() as cur:
                cur.execute("SHOW search_path;")
                path = cur.fetchone()
                print(f"[TENANT MIGRATION] DB search_path confirmed: {path}")

            # Migrate each tenant app individually so shared apps are NOT touched
            # CRITICAL: Re-activate the tenant schema BEFORE each app's migration.
            # Django's post_migrate signals (content types, permissions) fire after each
            # app migration and may reset the search_path back to 'public'.
            # Without this re-activation, the router sees 'public' schema for the next
            # app and blocks it, leaving the tenant without its tables.
            for app_label in TENANT_APPS:
                try:
                    # Force search_path back to tenant schema before each migration
                    with connection.cursor() as cur:
                        cur.execute(ACTIVATE_SCHEMA_SQL.format(schema_name=schema_name))
                    connection.schema_name = schema_name
                    print(f"[TENANT MIGRATION] Migrating app: {app_label} (confirmed schema: {schema_name})")
                    call_command(
                        "migrate",
                        app_label,
                        interactive=False,
                        verbosity=1,
                    )
                except Exception as app_err:
                    print(f"[TENANT MIGRATION] Warning: could not migrate '{app_label}': {app_err}")

            print(f"--- Successfully finished migrating {schema_name} ---")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[TENANT MIGRATION] Error during migration for {schema_name}: {e}")
    finally:
        # Crucial: ensure we close the connection OUTSIDE the context manager
        connection.close()