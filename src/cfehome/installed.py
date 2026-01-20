
SHARED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "accounts", 
    "allauth",
    "allauth.account",
    "tenants",
]

TENANT_APPS = [
    "accounts",
    "approvals",
    "attendance",
    "slippers",
    "widget_tweaks",
    "commando",
]

_INSTALLED_APPS = SHARED_APPS + [app for app in TENANT_APPS if app not in SHARED_APPS]

_CUSTOMER_INSTALLED_APPS = TENANT_APPS