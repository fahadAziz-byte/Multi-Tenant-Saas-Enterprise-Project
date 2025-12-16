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
from django.core.mail import send_mail
from django.conf import settings
from django.db import models
from datetime import date
from django.contrib.auth import get_user_model
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

class TenantLoginView(View):
    def get(self, request):
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
        if subdomain in ["localhost", None] or not request.subdomain:
            print(f"[LOGIN] Main domain login attempt for: {username}")
            
            from helpers.db.schemas import use_public_schema
            
            with use_public_schema(revert_schema_name=None, revert_schema=False):
                User = get_user_model()
            
            # 1. Check if user exists in this schema at all
            try:
                print(f"DEBUG: getting user from user model")
                debug_user = User.objects.get(username=username)
                print(f"DEBUG: User found in public schema. ID: {debug_user.pk}, Active: {debug_user.is_active}")
                
                # 2. Check password manually for debugging
                pass_check = debug_user.check_password(password)
                print(f"DEBUG: Password check result: {pass_check}")
                
            except User.DoesNotExist:
                print("DEBUG: User NOT found in public schema.")

            # 3. Proceed with standard auth
            print('authenticating user : ', username)
            user = authenticate(request, username=username, password=password)
            print('after authenticating user : ', user)
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
        if subdomain in ["localhost", None] or not request.subdomain:
            return render(request,'accounts/tenant/tenant_signup.html')
        else:
            from accounts.models import Department
            
            # This automatically queries from the active tenant schema
            departments = Department.objects.all().order_by('name')
            
            context = {
                'departments': departments,
                'tenant_name':request.subdomain
            }
            
            return render(request, 'accounts/signup.html', context)
    
    def post(self, request):
        
        host = request.get_host().split(':')[0]
        subdomain = host.split('.')[0]

        #for tenants signup post request
        if subdomain in ["localhost", None] or not request.subdomain:
            sub=request.POST.get('subdomain')
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')

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

            context={
                'subdomain':sub,
                'username':username,
                'tenant_url':f'http://{sub}.localhost:8000/users/tenant_homepage'
            }
            return render(request,'accounts/tenant/tenant_signup_success.html',context)



        if request.subdomain!=subdomain:
            request.subdomain=None
            tenant = get_tenant_from_subdomain(request)
            if not tenant:
                return HttpResponse("Sorry! You can only access by your enterprise subdomain")
            print("Went to public to findout out subdomain which is : ",tenant.subdomain)

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
            
            # Check if application already exists
            if EmployeeApproval.objects.filter(username=username).exists():
                return render(request, 'accounts/signup.html', {
                    'error': 'An employee application with this username already exists',
                    'departments': departments
                })
            
            if EmployeeApproval.objects.filter(email=email).exists():
                return render(request, 'accounts/signup.html', {
                    'error': 'An employee application with this email already exists',
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
            
            print(f"[EMPLOYEE APPLICATION] Created for {username} in {department.name}")
            
            # Send notification to HRs who manage this department
            from accounts.models import HRProfile
            
            # Get HRs who manage this department or admin HRs
            hrs_to_notify = HRProfile.objects.filter(
                models.Q(departments=department) | models.Q(is_admin=True)
            ).select_related('account__user').distinct()
            
            hr_emails = [hr.account.user.email for hr in hrs_to_notify if hr.account.user.email]
            
            if hr_emails:
                try:
                    send_mail(
                        subject=f'New Employee Application - {department.name}',
                        message=f'''
                            A new employee application has been submitted.

                            Applicant Details:
                            - Username: {username}
                            - Email: {email}
                            - Department: {department.name}

                            Please review and approve/reject this application in your HR dashboard.

                            Login to review: http://{request.subdomain}.localhost:8000/users/hr/employee-approvals/
                        ''',
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=hr_emails,
                        fail_silently=True,
                    )
                    print(f"[EMAIL] Notification sent to {len(hr_emails)} HRs")
                    print("HR mails are ",hr_emails)
                except Exception as e:
                    print(f"[ERROR] Failed to send email: {e}")
            
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
            
            # Get HR details
            is_admin = request.POST.get('is_admin') == 'true'
            
            # Create HR Approval Request
            hr_approval = HRApproval.objects.create(
                username=username,
                email=email,
                password_hash=make_password(password),
                first_name=first_name,
                last_name=last_name,
                is_admin=is_admin
            )
            
            # Assign requested departments (if not admin)
            if not is_admin:
                department_ids = request.POST.getlist('hr_departments')
                if department_ids:
                    departments_list = Department.objects.filter(id__in=department_ids)
                    hr_approval.requested_departments.set(departments_list)
            
            print(f"[HR APPLICATION] Created for {username}")
            
            # Send notification to tenant owner
            owner = User.objects.filter(is_superuser=True).first()
            if owner and owner.email:
                try:
                    send_mail(
                        subject=f'New HR Application - {username}',
                        message=f'''
                            A new HR application has been submitted.

                            Applicant Details:
                            - Username: {username}
                            - Email: {email}
                            - Type: {"Admin HR" if is_admin else "Department HR"}

                            Please review and approve/reject this application in your tenant dashboard.

                            Login to review: http://{request.subdomain}.localhost:8000/users/tenant/hr-approvals/
                        ''',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[owner.email],
                        fail_silently=True,
                    )
                    print(f"[EMAIL] Notification sent to owner: {owner.email}")
                except Exception as e:
                    print(f"[ERROR] Failed to send email: {e}")
            
            # Show success page
            return render(request, 'accounts/signup_success.html', {
                'username': username,
                'email': email,
                'role': 'HR',
                'tenant_name': request.subdomain,
                'approver': owner.username,
            })
        
        return redirect('loginn')
    


@login_required
def user_logout(request):
    """
    Logout the current user and redirect to login page
    """
    logout(request)
    return redirect('loginn')