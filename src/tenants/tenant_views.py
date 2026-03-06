from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Count, Q
from accounts.models import Account, Department, HRProfile, EmployeeProfile
from approvals.models import HRApproval
from datetime import datetime, timedelta
from helpers.db.schemas import use_public_schema,get_schema_name,activate_tenant_schema,use_tenant_schema
from django.conf import settings
from decouple import config
from .models import Tenants
PRODUCTION_BASE_URL=settings.PRODUCTION_BASE_URL
DEBUG = config("DJANGO_DEBUG", cast=bool, default=False)

def tenant_selection(request):
    """Show list of tenants owned by this user"""
    if not request.user.is_superuser:
        return HttpResponse("Access denied!")
    
    with use_public_schema(revert_schema_name=None, revert_schema=False):
        tenants = Tenants.objects.filter(owner=request.user)
    
    # If only one tenant, redirect directly
    if tenants.count() == 1:
        tenant = tenants.first()
        if DEBUG:
            return redirect(f"http://localhost:8000/users/tenant_homepage/{tenant.schema_name}")
        else:
            return redirect(f"https://{request.subdomain}.scalesphere.space/users/tenant_homepage/{tenant.schema_name}")
    context = {'tenants': tenants}
    return render(request, 'accounts/tenant/tenant_selection.html', context)


def tenant_home(request,schema_name):
    """Tenant owner dashboard"""
    if request.subdomain in ['localhost', settings.MAIN_SUBDOMAIN]:
        print("Accessing through ",request.subdomain)
    
    if not request.user.is_superuser:
        print('user : ',request.user)
        print('username : ',request.user.username)
        print('superuser : ',request.user.is_superuser)
        return HttpResponse("Access denied!")
    
    # if not request.user.is_superuser:
    #     return HttpResponse("Access denied! Only tenant owners can access this page.")
    
    try:
        with use_public_schema(revert_schema_name=schema_name,revert_schema=True):
            print("using public schema to get tenant model")
            from tenants.models import Tenants
            tenant_obj=Tenants.objects.get(schema_name=schema_name)
            print(f"got subdomain : {tenant_obj.subdomain} and schema name : {tenant_obj.schema_name}")


        # Get all departments with counts
        departments = Department.objects.annotate(
            employee_count=Count('employees', distinct=True),
            hr_count=Count('hr_managers', distinct=True)
        ).order_by('name')
        
        # Get pending HR applications
        pending_hr_approvals = HRApproval.objects.filter(status='PENDING').count()
        
        # Get statistics
        total_employees = EmployeeProfile.objects.count()
        total_hrs = HRProfile.objects.count()
        total_departments = departments.count()
        
        # Get recent activity (last 7 days)
        seven_days_ago = datetime.now() - timedelta(days=7)
        recent_employees = EmployeeProfile.objects.filter(
            account__user__date_joined__gte=seven_days_ago
        ).count()
        recent_hrs = HRProfile.objects.filter(
            account__user__date_joined__gte=seven_days_ago
        ).count()
        
        # Get tenant age
        tenant_age = (datetime.now().date() - tenant_obj.timestamp.date()).days
        
        # Get system health
        total_users = User.objects.count()
        active_users = User.objects.filter(last_login__isnull=False).count()
        
        context = {
            'schema_name': tenant_obj.schema_name,
            'tenant_name': tenant_obj.subdomain,
            'tenant_obj': tenant_obj,
            'username': request.user.username,
            'departments': departments,
            'pending_hr_approvals': pending_hr_approvals,
            'total_employees': total_employees,
            'total_hrs': total_hrs,
            'total_departments': total_departments,
            'recent_employees': recent_employees,
            'recent_hrs': recent_hrs,
            'tenant_age': tenant_age,
            'total_users': total_users,
            'active_users': active_users,
        }
        
        return render(request, 'accounts/tenant/tenant_homepage.html', context)
        
    except Exception as e:
        print(f"[ERROR] tenant_home: {str(e)}")
        import traceback
        traceback.print_exc()
        return HttpResponse(f"Error loading page: {str(e)}")


def hr_approval_list(request,schema_name):
    """View all pending HR applications"""
    if not request.subdomain or request.subdomain=='localhost' or request.subdomain==settings.MAIN_SUBDOMAIN:
        print("Accessing hr approval list for tenant owner though local host")
    
    if not request.user.is_superuser:
        return HttpResponse("Access denied! Only tenant owners can access this page.")
    
    try:
        # with use_public_schema(revert_schema_name=None,revert_schema=False):
        #     print("using public schema to get tenant model")
        #     from tenants.models import Tenants
        #     tenant_obj=Tenants.objects.get(owner=request.user)
        #     print(f"got subdomain : {tenant_obj.subdomain} and schema name : {tenant_obj.schema_name}")
        
        # schema_name,valid_tenant,subdomain=get_schema_name(subdomain=tenant_obj.subdomain)
        activate_tenant_schema(schema_name)

        # Get pending HR applications
        pending_hrs = HRApproval.objects.filter(status='PENDING').order_by('-applied_at')
        
        # Get recently reviewed applications (last 20)
        reviewed_hrs = HRApproval.objects.filter(
            status__in=['APPROVED', 'REJECTED']
        ).order_by('-reviewed_at')[:20]
        
        context = {
            'schema_name':schema_name,
            'tenant_name': 'Enterprise',
            'pending_hrs': pending_hrs,
            'reviewed_hrs': reviewed_hrs,
        }
        
        return render(request, 'accounts/tenant/hr_approval_list.html', context)
        
    except Exception as e:
        print(f"[ERROR] hr_approval_list: {str(e)}")
        import traceback
        traceback.print_exc()
        return HttpResponse(f"Error loading page: {str(e)}")


def hr_approval_detail(request,schema_name, application_id):
    """View and approve/reject HR application"""
    if request.subdomain=='localhost' or request.subdomain==settings.MAIN_SUBDOMAIN:
        print(f"Accessing hr approval detail through {request.subdomain}")
    
    if not request.user.is_superuser:
        print('user : ',request.user)
        print('username : ',request.user.username)
        print('superuser : ',request.user.is_superuser)
        return HttpResponse("Access denied!")
    # if not request.user.is_superuser:
    #     return HttpResponse("Access denied! Only tenant owners can access this page.")

    # with use_public_schema(revert_schema_name=None,revert_schema=False):
    #     print("using public schema to get tenant model")
    #     from tenants.models import Tenants
    #     tenant_obj=Tenants.objects.get(owner=request.user)
    #     print(f"got subdomain : {tenant_obj.subdomain} and schema name : {tenant_obj.schema_name}")
        
    # schema_name,valid_tenant,subdomain=get_schema_name(subdomain=tenant_obj.subdomain)
    with use_public_schema(revert_schema_name=schema_name, revert_schema=True):
        tenant_obj=Tenants.objects.get(schema_name=schema_name)
    
    try:
        hr_application = HRApproval.objects.get(id=application_id, status='PENDING')
        if request.method == 'POST':
            action = request.POST.get('action')
            
            if action == 'approve':
                # CREATE THE ACTUAL USER AND HR ACCOUNT
                user = User.objects.create(
                    username=hr_application.username,
                    email=hr_application.email,
                    first_name=hr_application.first_name,
                    last_name=hr_application.last_name
                )
                
                # Set the hashed password
                user.password = hr_application.password_hash
                user.save()
                
                print(f"[APPROVAL] User created: {user.username}")
                
                # Create HR account
                account = Account.objects.create(
                    user=user,
                    role='HR'
                )
                
                # Get HR profile (created by signal)
                hr_profile = HRProfile.objects.get(account=account)
                hr_profile.is_admin = hr_application.is_admin
                hr_profile.save()
                
                # Assign departments
                if not hr_application.is_admin:
                    requested_depts = hr_application.requested_departments.all()
                    hr_profile.departments.set(requested_depts)
                    dept_names = ", ".join([d.name for d in requested_depts])
                else:
                    dept_names = "All Departments"
                
                # Update application status
                hr_application.status = 'APPROVED'
                hr_application.reviewed_at = timezone.now()
                hr_application.save()
                
                print(f"[APPROVAL] HR account approved: {user.username}")
                
                # Send approval email
                try:
                    send_mail(
                        subject=f'HR Application Approved - {request.subdomain}',
                        message=f'''
Congratulations {hr_application.first_name}!

Your HR application has been APPROVED by {request.subdomain}.

✅ Account Details:
- Username: {user.username}
- Email: {user.email}
- Role: {"Admin HR (Full Access)" if hr_application.is_admin else f"Department HR ({dept_names})"}
- Organization: {request.subdomain}

🔗 Login here:
http://{request.subdomain}.localhost:8000/users/user-login/

Welcome to the team! You can now manage employee applications and attendance.

---
{request.subdomain} Administration Team
                        ''',
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[user.email],
                        fail_silently=False,
                    )
                    print(f"[EMAIL] Approval email sent to owner")
                except Exception as e:
                    print(f"[ERROR] Failed to send approval email: {e}")
                
                return redirect('hr-approval-list')
            
            elif action == 'reject':
                rejection_reason = request.POST.get('rejection_reason', 'Not specified')
                
                # Update application status
                hr_application.status = 'REJECTED'
                hr_application.reviewed_at = timezone.now()
                hr_application.rejection_reason = rejection_reason
                hr_application.save()
                
                print(f"[REJECTION] HR application rejected: {hr_application.username}")
                
                # Send rejection email
                try:
                    send_mail(
                        subject=f'HR Application Update - {request.subdomain}',
                        message=f'''
Dear {hr_application.first_name or hr_application.username},

Thank you for your interest in joining {request.subdomain} as an HR.

After careful review, we are unable to approve your application at this time.

Reason: {rejection_reason}

If you have any questions, please contact the organization administrator.

---
{request.subdomain} Administration Team
                        ''',
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[hr_application.email],
                        fail_silently=False,
                    )
                    print(f"[EMAIL] Rejection email sent to {hr_application.email}")
                except Exception as e:
                    print(f"[ERROR] Failed to send rejection email: {e}")
                
                # Delete the rejected application after email is sent
                hr_application.delete()
                
                return redirect('hr-approval-list')
        
        # Get requested departments
        managed_departments = hr_application.requested_departments.all()
        
        context = {
            'schema_name':schema_name,
            'tenant_name': 'Enterprise',
            'hr_application': hr_application,
            'managed_departments': managed_departments,
        }
        
        return render(request, 'accounts/tenant/hr_approval_detail.html', context)
        
    except HRApproval.DoesNotExist:
        return HttpResponse("HR application not found or already reviewed!")
    except Exception as e:
        print(f"[ERROR] hr_approval_detail: {str(e)}")
        import traceback
        traceback.print_exc()
        return HttpResponse(f"Error: {str(e)}")


def department_detail(request,schema_name, department_id):
    """View department details with HRs and Employees"""
    if not(request.subdomain=='localhost' or request.subdomain==settings.MAIN_SUBDOMAIN):
        return HttpResponse("Only tenant owners can access this page")

    print(f"You are accesing department detail through {request.subdomain}")
    
    if not request.user.is_superuser:
        print('user : ',request.user)
        print('username : ',request.user.username)
        print('superuser : ',request.user.is_superuser)
        return HttpResponse("Access denied!")

    try:
        # with use_public_schema(revert_schema_name=None,revert_schema=False):
        #     print("using public schema to get tenant model")
        #     from tenants.models import Tenants
        #     tenant_obj=Tenants.objects.get(owner=request.user)
        #     print(f"got subdomain : {tenant_obj.subdomain} and schema name : {tenant_obj.schema_name}")
            
        # schema_name,valid_tenant,subdomain=get_schema_name(subdomain=tenant_obj.subdomain)

        activate_tenant_schema(schema_name)
        department = Department.objects.get(id=department_id)
        
        # Get HRs managing this department
        hr_profiles = HRProfile.objects.filter(
            departments=department
        ).select_related('account__user')
        
        # Get admin HRs
        admin_hrs = HRProfile.objects.filter(
            is_admin=True
        ).select_related('account__user')
        
        # Get employees
        employees = EmployeeProfile.objects.filter(
            department=department
        ).select_related('account__user')
        
        context = {
            'schema_name':schema_name,
            'tenant_name': "Enterprise",
            'department': department,
            'hr_profiles': hr_profiles,
            'admin_hrs': admin_hrs,
            'employees': employees,
        }
        
        return render(request, 'accounts/department_detail.html', context)
        
    except Department.DoesNotExist:
        return HttpResponse("Department not found!")
    except Exception as e:
        print(f"[ERROR] department_detail: {str(e)}")
        import traceback
        traceback.print_exc()
        return HttpResponse(f"Error: {str(e)}")

@login_required
def department_create_view(request):
    from accounts.forms import DepartmentForm
    with use_public_schema(revert_schema_name=None, revert_schema=False):
        tenants = Tenants.objects.filter(owner=request.user)
    tenant_url=tenants[0].schema_name
    if request.method == "POST":
        with use_tenant_schema(schema_name=tenant_url,create_if_missing=False,revert_public=True):
            form = DepartmentForm(request.POST)
            if form.is_valid():
                # Django saves this to the CURRENT active tenant schema automatically
                form.save()
                print("[INFO] Department created successfully.")
        return redirect(f"https://{request.subdomain}.scalesphere.space/users/tenant_homepage/{tenant_url}")
    else:
        form = DepartmentForm()
    
    return render(request, "accounts/department_form.html", {"form": form,"tenant_url":tenant_url})
