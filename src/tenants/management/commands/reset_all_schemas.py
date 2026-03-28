"""
Management command: reset_all_schemas

⚠️  DANGER: This is a DESTRUCTIVE command. It will:
  1. Drop ALL tenant schemas from the database (all HR, employee, department data gone)
  2. Flush all data from the public schema tables (all tenant owner accounts gone)
  3. Keep the database structure intact so you can re-migrate cleanly

Usage:
    python manage.py reset_all_schemas
    python manage.py reset_all_schemas --confirm   (skip the confirmation prompt)

After running this, do:
    python manage.py migrate       (rebuild public schema tables)
    python manage.py createsuperuser  (if you need an admin)
"""

from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "⚠️ DESTRUCTIVE: Drop all tenant schemas and flush the public schema. Use to start from zero."

    def add_arguments(self, parser):
        parser.add_argument(
            "--confirm",
            action="store_true",
            help="Skip the confirmation prompt and run immediately.",
        )

    def handle(self, *args, **options):
        if not options["confirm"]:
            self.stdout.write(self.style.WARNING(
                "\n⚠️  WARNING: This will PERMANENTLY DELETE all tenant schemas and all public data.\n"
                "   This cannot be undone!\n"
            ))
            answer = input("Type 'yes' to continue: ").strip().lower()
            if answer != "yes":
                self.stdout.write("Aborted.")
                return

        # ─────────────────────────────────────────────────
        # STEP 1: Find all tenant schemas (non-system schemas)
        # ─────────────────────────────────────────────────
        self.stdout.write("\n[Step 1] Finding all tenant schemas...")
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT schema_name
                FROM information_schema.schemata
                WHERE schema_name NOT IN (
                    'public', 'information_schema', 'pg_catalog',
                    'pg_toast', 'pg_temp_1', 'pg_toast_temp_1'
                )
                AND schema_name NOT LIKE 'pg_%'
            """)
            tenant_schemas = [row[0] for row in cursor.fetchall()]

        if tenant_schemas:
            self.stdout.write(f"   Found {len(tenant_schemas)} tenant schema(s): {tenant_schemas}")
        else:
            self.stdout.write("   No tenant schemas found.")

        # ─────────────────────────────────────────────────
        # STEP 2: Drop each tenant schema with CASCADE
        # ─────────────────────────────────────────────────
        self.stdout.write("\n[Step 2] Dropping tenant schemas...")
        for schema in tenant_schemas:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE')
                self.stdout.write(self.style.SUCCESS(f"   ✓ Dropped schema: {schema}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"   ✗ Failed to drop schema '{schema}': {e}"))

        # ─────────────────────────────────────────────────
        # STEP 3: Reset the public schema
        # Drop all user-defined tables in public (keeps schema itself)
        # ─────────────────────────────────────────────────
        self.stdout.write("\n[Step 3] Finding all tables in public schema...")
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT tablename
                FROM pg_tables
                WHERE schemaname = 'public'
                ORDER BY tablename
            """)
            public_tables = [row[0] for row in cursor.fetchall()]

        self.stdout.write(f"   Found {len(public_tables)} table(s) in public: {public_tables}")

        self.stdout.write("\n[Step 4] Dropping all public schema tables...")
        if public_tables:
            try:
                with connection.cursor() as cursor:
                    # Drop all tables in one shot using CASCADE
                    tables_sql = ", ".join([f'"public"."{t}"' for t in public_tables])
                    cursor.execute(f"DROP TABLE IF EXISTS {tables_sql} CASCADE")
                self.stdout.write(self.style.SUCCESS(f"   ✓ Dropped all {len(public_tables)} table(s) from public schema."))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"   ✗ Failed to drop public tables: {e}"))
                self.stdout.write("   Trying one by one...")
                for table in public_tables:
                    try:
                        with connection.cursor() as cursor:
                            cursor.execute(f'DROP TABLE IF EXISTS "public"."{table}" CASCADE')
                        self.stdout.write(self.style.SUCCESS(f"     ✓ Dropped: {table}"))
                    except Exception as te:
                        self.stdout.write(self.style.ERROR(f"     ✗ Failed: {table} → {te}"))

        # ─────────────────────────────────────────────────
        # STEP 5: Summary
        # ─────────────────────────────────────────────────
        self.stdout.write(self.style.SUCCESS(
            f"\n{'='*60}\n"
            f"✅ Reset complete!\n\n"
            f"Next steps:\n"
            f"  1. python manage.py migrate          ← rebuild public schema\n"
            f"  2. python manage.py createsuperuser  ← create admin (optional)\n"
            f"{'='*60}\n"
        ))
