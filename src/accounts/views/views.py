from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from helpers.db.schemas import use_tenant_schema_for_auth,activate_tenant_schema
from tenants.models import Tenants
from accounts.models import Account,Department
from django.contrib.auth.decorators import login_required
from django.views import View
from django.http import HttpResponse
from django.conf import settings
from django.db import models
from datetime import date
from django.contrib.auth import get_user_model
from decouple import config
DEBUG = config("DJANGO_DEBUG", cast=bool, default=False)
PRODUCTION_BASE_URL=settings.PRODUCTION_BASE_URL
MAIN_SUBDOMAIN=settings.MAIN_SUBDOMAIN
# ============================
# Helper function to get tenant
# ============================

def get_tenant_from_subdomain(request):
    """Extract tenant from subdomain"""
    host = request.get_host().split(':')[0]
    subdomain = host.split('.')[0]
    
    if subdomain in ["localhost", None]:
        return None
    
    try:
        with use_tenant_schema_for_auth("public", False, False):
            tenant=Tenants.objects.get(subdomain=subdomain)
            request.subdomain=tenant.subdomain
            print("in with block with ",request.subdomain)
    except Tenants.DoesNotExist:
        return None
    finally:
        print("in finally block and activating subdomain : ",subdomain," which is also : ",request.subdomain)
        activate_tenant_schema(tenant.schema_name)
        return tenant


# ============================
# Simple Login View
# ============================

from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator

@method_decorator(ensure_csrf_cookie, name='dispatch')
class TenantLoginView(View):
    def get(self, request):
        print("IS_SECURE:", request.is_secure())
        print("SCHEME:", request.scheme)
        print("HOST:", request.get_host())

        return render(request, 'accounts/login.html')
    
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Get the 'next' parameter (where to redirect after login)
        next_url = request.GET.get('next') or request.POST.get('next')
        
        # Check if we're on a subdomain or main domain
        host = request.get_host().split(':')[0]
        subdomain = host.split('.')[0]
        
        # ==========================================
        # MAIN DOMAIN LOGIN (Tenant Owner)
        # ==========================================
        if subdomain in ["localhost", settings.MAIN_SUBDOMAIN, None] or not request.subdomain:
            print(f"[LOGIN] Main domain login attempt for: {username}")
            
            
            User = get_user_model()
            
            
            user = authenticate(request, username=username, password=password)
            print('after authenticating user : ', username)
            if user is not None and user.is_superuser:
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                print(f"[LOGIN] Tenant owner logged in: {username}")
                
                # Redirect to tenant selection/dashboard
                if next_url:
                    return redirect(next_url)
                return redirect('tenant-selection')  # this view is from tenants.tenant_views.tenant_selection
            else:
                return render(request, 'accounts/login.html', {
                    'error': 'Invalid credentials or not a tenant owner.'
                })
        
        # ==========================================
        # SUBDOMAIN LOGIN (HR/Employee)
        # ==========================================
        else:
            print(f"[LOGIN] Subdomain login attempt for: {username} on {request.subdomain}")
            
            # Authenticate in tenant schema (already activated by middleware)
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                print(f"[LOGIN] Authentication successful for {username}")
                
                # Login the user
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                
                # Check user role and redirect
                try:
                    account = Account.objects.get(user=user)
                    print(f"[LOGIN] User role: {account.role}")
                    print(f'Request User before assigning it {request.user}')

                    
                    # If there's a 'next' parameter, redirect there
                    if next_url:
                        return redirect(next_url)
                    
                    # Otherwise, redirect based on role
                    if account.role.upper() == "EMPLOYEE":
                        return redirect('employee_home')
                    elif account.role.upper() == "HR":
                        return redirect('hr_home')
                    else:
                        return HttpResponse("Unknown role!")
                except Account.DoesNotExist:
                    return HttpResponse("Account not found! Please contact your administrator.")
            else:
                print(f"[LOGIN] Authentication FAILED for {username}")
                return render(request, 'accounts/login.html', {
                    'error': 'Invalid username or password'
                })

# ============================
# Simple Signup View
# ============================

class TenantSignupView(View):
    def get(self, request):
        # Tenant already set by middleware, schema already activated
        if not request.subdomain:
            return HttpResponse("Sorry! You can only signup by your enterprise subdomain")
        
        host = request.get_host().split(':')[0]
        subdomain = host.split('.')[0]

        #for tenants signup get page
        if subdomain in ["localhost", settings.MAIN_SUBDOMAIN] or not request.subdomain:
            return render(request,'accounts/tenant/tenant_signup.html')
        else:
            from accounts.models import Department
            
            # Query departments
            departments = Department.objects.all().order_by('name')
            
            # Check if any departments exist
            is_sign_up_allowed = departments.exists()
            
            message = ""
            if not is_sign_up_allowed:
                message = "No department is available for employees or HRs to signup. No HRs or employees will be able to sign up until the tenant owner creates a department."
            
            context = {
                'departments': departments,
                'tenant_name': request.subdomain,
                'isSignUpAllowed': is_sign_up_allowed,
                'message': message
            }
            
            return render(request, 'accounts/signup.html', context)
    
    def post(self, request):
        
        host = request.get_host().split(':')[0]
        subdomain = host.split('.')[0]

        #for tenants signup post request
        if subdomain in ["localhost", settings.MAIN_SUBDOMAIN] or not request.subdomain:
            sub=request.POST.get('subdomain')
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')

            if User.objects.filter(username=username).exists():
                return render(request, 'accounts/tenant/tenant_signup.html', {
                    'error': 'Username already exists',
                    'departments': None
                })
    
            if User.objects.filter(email=email).exists():
                return render(request, 'accounts/tenant/tenant_signup.html', {
                    'error': 'Email already exists',
                    'departments': None
                })
            newUser=User.objects.create(
                username=username,
                email=email,
                password=make_password(password),
                is_superuser=True,
            )
            from tenants.models import Tenants

            newTenantObj=Tenants.objects.create(
                owner=newUser,
                subdomain=sub,
            )
            if DEBUG:
                tenant_url=f'http://localhost:8000/users/tenant_homepage/{newTenantObj.schema_name}'
            else:
                tenant_url=f'https://{subdomain}.scalesphere.space/users/tenant_homepage/{newTenantObj.schema_name}'
            context={
                'subdomain':sub,
                'username':username,
                'tenant_url':tenant_url
            }
            return render(request,'accounts/tenant/tenant_signup_success.html',context)



        if request.subdomain!=subdomain:
            request.subdomain=None
            tenant = get_tenant_from_subdomain(request)
            if not tenant:
                return HttpResponse("Sorry! You can only access by your enterprise subdomain")
            print("Went to public to findout out subdomain which is : ",request.subdomain)

        username = request.POST.get('username')
        first_name=request.POST.get('first_name')
        last_name=request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')

        
    
        departments = Department.objects.all().order_by('name')
   # Check if username/email already exists in actual User table
        if User.objects.filter(username=username).exists():
            return render(request, 'accounts/signup.html', {
                'error': 'Username already exists',
                'departments': departments
            })
        
        if User.objects.filter(email=email).exists():
            return render(request, 'accounts/signup.html', {
                'error': 'Email already exists',
                'departments': departments
            })
        
        # ==========================================
        # EMPLOYEE SIGNUP - Needs HR Approval
        # ==========================================
        if role.lower() == "employee":
            from approvals.models import EmployeeApproval
            from accounts.models import EmployeeProfile

            # Check if username already exists
            if (EmployeeApproval.objects.filter(username=username).exists() or 
                EmployeeProfile.objects.filter(account__user__username=username).exists()):
                return render(request, 'accounts/signup.html', {
                    'error': 'An employee application or account with this username already exists',
                    'departments': departments
                })

            # Check if email already exists
            if (EmployeeApproval.objects.filter(email=email).exists() or 
                EmployeeProfile.objects.filter(account__user__email=email).exists()):
                return render(request, 'accounts/signup.html', {
                    'error': 'An employee application or account with this email already exists',
                    'departments': departments
                })
            
            # Get department
            department_id = request.POST.get('department')
            if not department_id:
                return render(request, 'accounts/signup.html', {
                    'error': 'Please select a department',
                    'departments': departments
                })
            
            department = Department.objects.get(id=department_id)
            
            # Create Employee Approval Request
            employee_approval = EmployeeApproval.objects.create(
                username=username,
                email=email,
                password_hash=make_password(password),
                first_name=first_name,
                last_name=last_name,
                department=department
            )
            
            
            
            # Show success page
            return render(request, 'accounts/signup_success.html', {
                'username': username,
                'email': email,
                'role': 'Employee',
                'tenant_name': request.subdomain,
                'approver': 'HR'
            })
        
        # ==========================================
        # HR SIGNUP - Needs Tenant Owner Approval
        # ==========================================
        elif role.lower() == "hr":
            from approvals.models import HRApproval
            from accounts.models import HRProfile
            # Check if application already exists
            if HRApproval.objects.filter(username=username).exists():
                return render(request, 'accounts/signup.html', {
                    'error': 'An HR application with this username already exists',
                    'departments': departments
                })
            
            if HRApproval.objects.filter(email=email).exists():
                return render(request, 'accounts/signup.html', {
                    'error': 'An HR application with this email already exists',
                    'departments': departments
                })
            
            if HRProfile.objects.filter(account__user__username=username).exists():
                return render(request, 'accounts/signup.html', {
                    'error': 'An HR account with this username already exists',
                    'departments': departments
                })
            
            if HRProfile.objects.filter(account__user__email=email).exists():
                return render(request, 'accounts/signup.html', {
                    'error': 'An HR account with this email already exists',
                    'departments': departments
                })
            
            # Get HR details
            is_admin = request.POST.get('is_admin') == 'true'
            
            # Create HR Approval Request
            # ===== DEBUG: log active schema at HR signup time =====
            from django.db import connection as dbconn
            _schema_at_signup = getattr(dbconn, 'schema_name', 'UNKNOWN')
            with dbconn.cursor() as _cur:
                _cur.execute("SHOW search_path;")
                _db_path = _cur.fetchone()
            print(f"[DEBUG HR SIGNUP] request.subdomain = '{request.subdomain}'")
            print(f"[DEBUG HR SIGNUP] connection.schema_name = '{_schema_at_signup}'")
            print(f"[DEBUG HR SIGNUP] Postgres SHOW search_path = {_db_path}")
            # ===== END DEBUG =====
            hr_approval = HRApproval.objects.create(
                username=username,
                email=email,
                password_hash=make_password(password),
                first_name=first_name,
                last_name=last_name,
                is_admin=is_admin
            )
            print(f"[DEBUG HR SIGNUP] HRApproval created with id={hr_approval.id} on schema '{_schema_at_signup}'")
            
            # Assign requested departments (if not admin)
            if not is_admin:
                department_ids = request.POST.getlist('hr_departments')
                if department_ids:
                    departments_list = Department.objects.filter(id__in=department_ids)
                    hr_approval.requested_departments.set(departments_list)
            
            print(f"[HR APPLICATION] Created for {username}")
            
            # Show success page
            return render(request, 'accounts/signup_success.html', {
                'username': username,
                'email': email,
                'role': 'HR',
                'tenant_name': request.subdomain,
                'approver': 'the Tenant Owner',
            })
        
        return redirect('loginn')
    


@login_required
def user_logout(request):
    """
    Logout the current user and redirect to login page
    """
    logout(request)
    return redirect('loginn')