# 1. SHARED_APPS: Always active, provides the Global User/Login
SHARED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "accounts",    # USER stays in PUBLIC via the Router
    "allauth",
    "allauth.account",
    "tenants",
    # ... any others ...
]

# 2. TENANT_APPS: What migrations run when a new tenant house is built
TENANT_APPS = [
    "accounts",    # DEPARTMENTS will be created in TENANT via the Router
    "approvals",
    "attendance",
    "slippers",
    "widget_tweaks",
    "commando",
]

# 3. Merged list for Django
_INSTALLED_APPS = SHARED_APPS + [app for app in TENANT_APPS if app not in SHARED_APPS]

# 4. Used by your migration task
_CUSTOMER_INSTALLED_APPS = TENANT_APPS