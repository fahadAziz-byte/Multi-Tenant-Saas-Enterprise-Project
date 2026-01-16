import pathlib
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings

from django.http import HttpResponse

LOGIN_URL = settings.LOGIN_URL

this_dir = pathlib.Path(__file__).resolve().parent

#hello claude can you give me front page for my website i mean when user simply types my website i should display something there i mean it should be beautiful and also tells what out website provides for enterprise and their owners and their employees and hrs and how we validate them and we switch tenants please make it look professional and also an option to signup and instruction for employees and hrs if the current request has no subdomain then it should show for employees and hrs to login with their enterprise subdomain  with following logicclass 
def LandingPageView(request):
    """Main landing page for the platform"""
    is_main_domain = False 
    if request.subdomain:
        if request.subdomain in ['localhost', settings.MAIN_SUBDOMAIN]:
            is_main_domain=True
    context = { 'is_main_domain': is_main_domain, 'subdomain': request.subdomain }
    return render(request, 'accounts/landing_page.html', context)
