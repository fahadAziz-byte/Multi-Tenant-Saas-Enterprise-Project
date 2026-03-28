from django.apps import apps
from cfehome.installed import SHARED_APPS, TENANT_APPS


class TenantSyncRouter:
    """
    Controls which apps' migrations run in:
      - public schema  (shared infrastructure: auth, tenants, accounts, etc.)
      - tenant schemas (per-tenant data: approvals, attendance, etc.)

    IMPORTANT: During management commands like `migrate`, the SchemaTenantMiddleware
    does NOT run (no HTTP request). So `connection.schema_name` is never set by
    middleware. We rely ONLY on the value explicitly set by our schema context managers
    (activate_tenant_schema / use_tenant_schema).

    If schema_name is 'public' OR unset → we are migrating the public schema.
    If schema_name is anything else     → we are migrating a tenant schema.
    """

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        from django.db import connection

        current_schema = getattr(connection, "schema_name", "public")

        # Treat None or unset as public (management commands have no middleware)
        if not current_schema:
            current_schema = "public"

        try:
            app_name = apps.get_app_config(app_label).name
        except LookupError:
            app_name = app_label

        is_shared = app_name in SHARED_APPS or app_label in SHARED_APPS
        is_tenant = app_name in TENANT_APPS or app_label in TENANT_APPS

        if current_schema == "public":
            # On public schema: only run shared app migrations
            # Apps in BOTH lists (like 'accounts') are allowed on public
            return is_shared
        else:
            # On a tenant schema: only run tenant app migrations
            # Apps in BOTH lists (like 'accounts') are allowed on tenant schemas too
            return is_tenant
