from django.db import connection

class TenantSyncRouter:
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # Identify if we are currently in the public schema
        # (This assumes your schema switcher sets connection.schema_name)
        active_schema = getattr(connection, 'schema_name', 'public')
        is_public = active_schema == 'public'

        if app_label == 'accounts':
            global_models = [
                'account', 'user', 'session', 
                'emailaddress', 'socialaccount', 'socialtoken', 'socialapp'
            ]
            
            if model_name in global_models:
                # ONLY create User/Auth tables if we are in Public
                return is_public
            else:
                # ONLY create Departments/Profiles if we are in a Tenant
                return not is_public

        # For all other apps (approvals, attendance), they only live in Tenants
        # So skip them if we are in public
        tenant_only_apps = ['approvals', 'attendance', 'commando']
        if app_label in tenant_only_apps:
            return not is_public

        return None