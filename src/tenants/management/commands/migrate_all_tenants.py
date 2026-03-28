"""
Management command: migrate_all_tenants

Re-runs tenant-specific migrations on ALL existing tenant schemas.
This is the fix when new apps (like 'approvals') are added to TENANT_APPS
but their tables were never created inside existing tenant schemas.

Usage:
    python manage.py migrate_all_tenants
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
from helpers.db.schemas import use_tenant_schema, does_schema_exists


class Command(BaseCommand):
    help = "Run tenant-app migrations on every existing tenant schema."

    def handle(self, *args, **options):
        # Import here to avoid AppRegistryNotReady
        from tenants.models import Tenants
        from helpers.db.schemas import activate_tenant_schema

        # Fetch all tenants from the public schema
        with connection.cursor() as cursor:
            cursor.execute('SET search_path TO "public"')
            connection.schema_name = "public"

        tenants = Tenants.objects.all()
        total = tenants.count()
        self.stdout.write(f"Found {total} tenant(s) to migrate.\n")

        success_count = 0
        fail_count = 0

        for tenant in tenants:
            schema = tenant.schema_name
            self.stdout.write(f"\n[{success_count + fail_count + 1}/{total}] Migrating schema: {schema} (subdomain: {tenant.subdomain})")

            if not does_schema_exists(schema):
                self.stdout.write(self.style.WARNING(f"  ⚠  Schema '{schema}' does not exist in DB — skipping."))
                fail_count += 1
                continue

            try:
                with use_tenant_schema(schema_name=schema, create_if_missing=False, revert_public=True):
                    self.stdout.write(f"  → search_path set to '{schema}'. Running migrations...")
                    call_command(
                        "migrate",
                        interactive=False,
                        verbosity=1,
                    )
                self.stdout.write(self.style.SUCCESS(f"  ✓ Done: {schema}"))
                success_count += 1
            except Exception as e:
                import traceback
                self.stdout.write(self.style.ERROR(f"  ✗ FAILED for {schema}: {e}"))
                traceback.print_exc()
                fail_count += 1

        self.stdout.write(
            f"\n{'='*60}\n"
            f"Migration complete: {success_count} succeeded, {fail_count} failed.\n"
        )
