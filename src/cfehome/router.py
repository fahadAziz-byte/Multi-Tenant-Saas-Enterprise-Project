# cfehome/router.py

class TenantSyncRouter:
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'accounts':
            # EVERYTHING listed here will stay in the Public (Main) DB
            # NOTHING here will be created inside the Tenants
            global_models = [
                'account',     # Your custom user class
                'user',        # Standard fallback
                'session', 
                'emailaddress', # If using AllAuth
                'socialaccount' # If using AllAuth
            ]
            if model_name in global_models:
                return True # Put in Public
            
            # EVERYTHING else in accounts (like 'department') 
            # will return False here, so it WON'T go into Public.
            # Instead, it will wait for your task to put it in the Tenant.
            return False 
            
        return None