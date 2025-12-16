DEFAULT_APPS = [
     # django-apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # third-party-apps
    "allauth_ui",
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.github',
    'slippers',
    "widget_tweaks",
    # app for both tenant and HR/Employees
    "accounts",
    'approvals',
]

# tenant/enterpise apps
_CUSTOMER_INSTALLED_APPS = DEFAULT_APPS + [
    # my-apps
    "commando",
    "attendance"
]
# reverse("tenants:list")

# public schema default installed apps
_INSTALLED_APPS = _CUSTOMER_INSTALLED_APPS + [
    # my-apps
    "commando",
    "tenants",
]

_INSTALLED_APPS = list(set(_INSTALLED_APPS))