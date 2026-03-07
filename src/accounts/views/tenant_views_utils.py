from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
from accounts.models import Account, Department, HRProfile, EmployeeProfile
from django.db.models import Count, Q
from decouple import config
from helpers.db.schemas import use_public_schema
from tenants.models import Tenants

@login_required
def department_detail(request, department_id):
    """View showing HRs and Employees of a specific department"""
    if not request.subdomain:
        return HttpResponse("Sorry! You can only access by your enterprise subdomain")
    
    try:
        account = Account.objects.get(user=request.user)
        
        if not request.user.is_superuser:
            return HttpResponse("Access denied! Only tenant owners can access this page.")
        
        # Get the department
        department = Department.objects.get(id=department_id)
        
        # Get HRs managing this department (only approved)
        hr_profiles = HRProfile.objects.filter(
            departments=department,
            account__is_approved=True
        ).select_related('account__user')
        
        # Get admin HRs (they manage all departments)
        admin_hrs = HRProfile.objects.filter(
            is_admin=True,
            account__is_approved=True
        ).select_related('account__user')
        
        # Get employees in this department
        employees = EmployeeProfile.objects.filter(
            department=department
        ).select_related('account__user')
        
        context = {
            'tenant_name': request.subdomain,
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
        return HttpResponse(f"Error loading page: {str(e)}")


@login_required
def hr_approval_list(request):
    """View all pending HR signup requests"""
    if not request.subdomain:
        return HttpResponse("Sorry! You can only access by your enterprise subdomain")
    
    try:
        account = Account.objects.get(user=request.user)
        
        if not request.user.is_superuser:
            return HttpResponse("Access denied! Only tenant owners can access this page.")
        
        # Get pending HR accounts
        pending_hrs = Account.objects.filter(
            role='HR',
            is_approved=False
        ).select_related('user', 'hrprofile').order_by('-user__date_joined')
        
        # Get approved/rejected HRs (recent 20)
        reviewed_hrs = Account.objects.filter(
            role='HR',
            is_approved=True
        ).select_related('user', 'hrprofile', 'approved_by').order_by('-approved_at')[:20]
        
        context = {
            'tenant_name': request.subdomain,
            'pending_hrs': pending_hrs,
            'reviewed_hrs': reviewed_hrs,
        }
        
        return render(request, 'accounts/hr_approval_list.html', context)
        
    except Account.DoesNotExist:
        return HttpResponse("Account not found!")
    except Exception as e:
        print(f"[ERROR] hr_approval_list: {str(e)}")
        import traceback
        traceback.print_exc()
        return HttpResponse(f"Error loading page: {str(e)}")



@login_required
def hr_approval_detail(request, account_id):
    """View detailed HR request and approve/reject"""
    if not request.subdomain:
        return HttpResponse("Sorry! You can only access by your enterprise subdomain")
    
    try:
        
        if not request.user.is_superuser:
            return HttpResponse("Access denied! Only tenant owners can access this page.")
        
        # Get the HR account
        hr_account = Account.objects.get(id=account_id, role='HR')
        hr_profile = HRProfile.objects.get(account=hr_account)
        
        # Handle approval/rejection
        if request.method == 'POST':
            action = request.POST.get('action')
            
            if action == 'approve':
                hr_account.is_approved = True
                hr_account.approved_by = request.user.username
                hr_account.approved_at = timezone.now()
                hr_account.save()
                
                
                print(f"[APPROVAL] HR {hr_account.user.username} approved by {request.user.username}")
                
                return redirect('hr-approval-list')
                
            elif action == 'reject':
                # Delete the account and user
                user = hr_account.user
                hr_account.delete()
                user.delete()
                
                print(f"[REJECTION] HR application rejected and deleted")
                
                return redirect('hr-approval-list')
        
        # Get departments this HR wants to manage
        managed_departments = hr_profile.departments.all()
        
        context = {
            'tenant_name': request.subdomain,
            'hr_account': hr_account,
            'hr_profile': hr_profile,
            'managed_departments': managed_departments,
        }
        
        return render(request, 'accounts/hr_approval_detail.html', context)
        
    except Account.DoesNotExist:
        return HttpResponse("HR account not found!")
    except Exception as e:
        print(f"[ERROR] hr_approval_detail: {str(e)}")
        import traceback
        traceback.print_exc()
        return HttpResponse(f"Error loading page: {str(e)}")