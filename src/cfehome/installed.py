# 1. SHARED_APPS: Only for the Public schema (Global things)
SHARED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    
    # User / Auth
    "accounts", # Your custom user app should stay shared for global login
    "allauth_ui",
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.github',
    
    # The management app
    "tenants", 
]

# 2. TENANT_APPS: Only for the specific client schemas
TENANT_APPS = [
    "slippers",
    "widget_tweaks",
    "approvals",
    "commando",
    "attendance",
    # Note: 'accounts' is NOT here because users are shared platform-wide
]

# 3. Final Production list for Django settings
# django-tenants (and similar engines) use these specifically
_INSTALLED_APPS = SHARED_APPS + [app for app in TENANT_APPS if app not in SHARED_APPS]

# FOR THE TENANT SCHEMA
_CUSTOMER_INSTALLED_APPS = TENANT_APPS