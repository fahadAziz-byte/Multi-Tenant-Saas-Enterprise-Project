from django.apps import apps
from cfehome.installed import SHARED_APPS, TENANT_APPS

class TenantSyncRouter:
    """
    A router to control which applications' models are created in the public schema
    versus the tenant schemas.
    """
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        from django.db import connection
        
        current_schema = getattr(connection, "schema_name", "public")
        
        try:
            app_name = apps.get_app_config(app_label).name
        except LookupError:
            app_name = app_label
            
        is_shared = app_name in SHARED_APPS or app_label in SHARED_APPS
        is_tenant = app_name in TENANT_APPS or app_label in TENANT_APPS

        if current_schema == "public":
            return is_shared
        else:
            return is_tenant
