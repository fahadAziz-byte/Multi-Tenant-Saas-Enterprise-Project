from django.db import connection
from helpers.db.statements import CREATE_SCHEMA_SQL, ACTIVATE_SCHEMA_SQL


# These are the app labels whose models should be created fresh in each tenant schema.
# - 'accounts'   : Department, Account, EmployeeProfile, HRProfile (per-tenant)
# - 'approvals'  : HRApproval, EmployeeApproval (per-tenant)
# - 'attendance' : Attendance, AttendanceRequest (per-tenant)
#
# We do NOT include shared-only apps (auth, contenttypes, sessions, tenants)
# because those tables already live in the public schema and are accessible via
# search_path fallback. Creating them again in the tenant schema would shadow
# the public tables and cause FK inconsistencies.
TENANT_APP_LABELS = ['accounts', 'approvals', 'attendance']


def migrate_single_tenant_task(tenant_id: str):
    """
    Create all tenant-specific tables in a new tenant schema using Django's
    SchemaEditor directly.

    WHY NOT call_command("migrate")?
    Django tracks migration history in a single shared `django_migrations` table
    in the public schema.  Once an app's migrations have run for ANY tenant,
    Django considers them "already applied" for every subsequent tenant and says
    "No migrations to apply" — leaving every new tenant with an empty schema.

    SchemaEditor.create_model() bypasses migration history entirely and directly
    creates the tables in the currently active schema, which is exactly what we need.
    """
    from django.apps import apps as django_apps

    Tenants = django_apps.get_model('tenants', 'Tenants')
    instance = Tenants.objects.get(id=tenant_id)
    schema_name = instance.schema_name

    print(f"[TENANT SETUP] Starting table creation for schema: {schema_name}")

    try:
        # ── Step 1: Create the Postgres schema if it doesn't exist ──────────
        with connection.cursor() as cursor:
            cursor.execute(CREATE_SCHEMA_SQL.format(schema_name=schema_name))
        print(f"[TENANT SETUP] Schema ensured: {schema_name}")

        # ── Step 2: Activate the tenant schema (set search_path) ────────────
        with connection.cursor() as cursor:
            cursor.execute(ACTIVATE_SCHEMA_SQL.format(schema_name=schema_name))
        connection.schema_name = schema_name

        # Confirm search_path
        with connection.cursor() as cursor:
            cursor.execute("SHOW search_path;")
            path = cursor.fetchone()
        print(f"[TENANT SETUP] search_path confirmed: {path}")

        # ── Step 3: Create all tenant model tables using SchemaEditor ────────
        # SchemaEditor.create_model() creates tables directly in the active schema.
        # FK constraints are deferred and executed in __exit__, so all models
        # must be created within the same `with schema_editor()` block.
        created = []
        skipped = []
        failed = []

        with connection.schema_editor() as schema_editor:
            for app_label in TENANT_APP_LABELS:
                try:
                    app_config = django_apps.get_app_config(app_label)
                    for model in app_config.get_models():
                        table = model._meta.db_table
                        try:
                            schema_editor.create_model(model)
                            created.append(table)
                            print(f"[TENANT SETUP] ✓ Created table: {table}")
                        except Exception as e:
                            msg = str(e).lower()
                            if "already exists" in msg or "duplicate" in msg:
                                skipped.append(table)
                                print(f"[TENANT SETUP] → Table already exists: {table}")
                            else:
                                failed.append(table)
                                print(f"[TENANT SETUP] ✗ Failed to create {table}: {e}")
                except LookupError:
                    print(f"[TENANT SETUP] ✗ App not found: {app_label}")

        print(
            f"[TENANT SETUP] Done for schema '{schema_name}': "
            f"{len(created)} created, {len(skipped)} skipped, {len(failed)} failed."
        )
        if failed:
            print(f"[TENANT SETUP] Failed tables: {failed}")

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[TENANT SETUP] ERROR for schema '{schema_name}': {e}")
    finally:
        # Always close so the next request gets a fresh connection
        connection.close()