from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from datetime import date
from .views import get_tenant_from_subdomain
from accounts.models import HRProfile, EmployeeProfile,Account,Department
from attendance.models import Attendance, AttendanceRequest
from datetime import datetime, timedelta
from django.db.models import Count
from django.conf import settings


# ============================
# Role-Based Home Views
# ============================


@login_required
def tenant_home(request):
    """Tenant owner dashboard showing departments overview"""
    if not (request.subdomain=="localhost" or request.subdomain==settings.MAIN_SUBDOMAIN):
        return HttpResponse("Sorry! You can only access by your main domain")
    
    try:
        account = Account.objects.get(user=request.user)
        
        # Check if user is tenant owner (you might have a different way to check this)
        # For now, let's assume there's a field or we check if they're a superuser
        if not request.user.is_superuser:
            return HttpResponse("Access denied! Only tenant owners can access this page.")
        
        # Get all departments with employee and HR counts
        departments = Department.objects.annotate(
            employee_count=Count('employees', distinct=True),
            hr_count=Count('hr_managers', distinct=True)
        ).order_by('name')
        
        # Get pending HR approvals
        pending_hr_approvals = Account.objects.filter(
            role='HR',
            is_approved=False
        ).select_related('user').count()
        
        # Get statistics
        total_employees = EmployeeProfile.objects.count()
        total_hrs = HRProfile.objects.filter(account__is_approved=True).count()
        total_departments = departments.count()
        
        context = {
            'tenant_name': request.subdomain,
            'username': request.user.username,
            'departments': departments,
            'pending_hr_approvals': pending_hr_approvals,
            'total_employees': total_employees,
            'total_hrs': total_hrs,
            'total_departments': total_departments,
        }
        
        return render(request, 'accounts/tenant/tenant_home.html', context)
        
    except Account.DoesNotExist:
        return HttpResponse("Account not found!")
    except Exception as e:
        print(f"[ERROR] tenant_home: {str(e)}")
        import traceback
        traceback.print_exc()
        return HttpResponse(f"Error loading page: {str(e)}")



def employee_home(request):
    host = request.get_host().split(':')[0]
    subdomain = host.split('.')[0]
    if request.subdomain in ["localhost", settings.MAIN_SUBDOMAIN]:
        return HttpResponse("Sorry! You can only access by your enterprise subdomain")
    
    try:
        print(f'Request User before accessing employee account {request.user}')
        account = Account.objects.get(user=request.user)
        if account:
            if account.role.upper() != "EMPLOYEE":
                return HttpResponse("Access denied! You are not authorized as an employee to access this page.")
        elif not account:
            return HttpResponse("Access denied! You are not authorized as an employee to access this page.")
        
        
        employee_profile = EmployeeProfile.objects.get(account=account)
        
       
        
        today = datetime.now().date()
        first_day = today.replace(day=1)
        
        # Get all attendance records for current month
        attendance_records = Attendance.objects.filter(
            employee=employee_profile,
            date__gte=first_day,
            date__lte=today
        ).order_by('date')
        
        # Calculate attendance percentage
        total_days = attendance_records.count()
        present_days = attendance_records.filter(status='PRESENT').count()
        attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0
        
        # Get leave balance
        leave_balance = employee_profile.total_leaves
        
        context = {
            'role':'employee',
            'tenant_name':subdomain,
            'username': request.user.username,
            'leave_balance': leave_balance,
            'attendance': round(attendance_percentage, 1),
            'attendance_records': attendance_records,
            'total_days': total_days,
            'present_days': present_days,
            'current_month': today.strftime('%B %Y'),
        }
        
        return render(request, 'accounts/emp/employee_home.html', context)
    except Account.DoesNotExist:
        return HttpResponse("Account not found!")
    except Exception as e:
        print(f"[ERROR] employee_home: {str(e)}")
        import traceback
        traceback.print_exc()
        return HttpResponse(f"Error loading page: {str(e)}")



def hr_home(request):
    # Tenant already set by middleware - no need for manual checks
    if request.subdomain in ["localhost", settings.MAIN_SUBDOMAIN]:
        return HttpResponse("Sorry! You can only access by your enterprise subdomain")
    
    try:
        print(f'Request User before accessing hr account {request.user}')
        account = Account.objects.get(user=request.user)
        if account:
            if account.role.upper() != "HR":
                return HttpResponse("Access denied! You are not authorized as an HR to access this page.")
        elif not account:
            return HttpResponse("Access denied! You are not an HR.")
        
        hr_profile = HRProfile.objects.get(account=account)
        
        # Filter employees based on HR's department access
        if hr_profile.is_admin or not hr_profile.departments.exists():
            # Admin HR or HR with no departments = see all employees
            accessible_employees = EmployeeProfile.objects.all()
            total_employees = accessible_employees.count()
        else:
            # Regular HR sees only their department's employees
            hr_departments = hr_profile.departments.all()
            accessible_employees = EmployeeProfile.objects.filter(
                department__in=hr_departments
            )
            total_employees = accessible_employees.count()
        
        # Get pending requests (only for accessible employees)
        pending_requests = AttendanceRequest.objects.filter(
            status='PENDING',
            employee__in=accessible_employees
        ).count()
        
        # Get today's attendance summary (only for accessible employees)
        today = date.today()
        today_attendance = Attendance.objects.filter(
            date=today,
            employee__in=accessible_employees
        )
        present_today = today_attendance.filter(status='PRESENT').count()
        absent_today = today_attendance.filter(status='ABSENT').count()
        on_leave_today = today_attendance.filter(status='LEAVE').count()
        not_marked_today = total_employees - (present_today + absent_today + on_leave_today)
        
        # Get recent attendance requests (only for accessible employees)
        recent_requests = AttendanceRequest.objects.filter(
            status='PENDING',
            employee__in=accessible_employees
        ).select_related('employee__account__user', 'employee__department')[:5]
        
        # Get department info for display
        if hr_profile.is_admin:
            managed_departments = "All Departments (Admin)"
        elif not hr_profile.departments.exists():
            managed_departments = "All Departments"
        else:
            dept_names = [dept.name for dept in hr_profile.departments.all()]
            managed_departments = ", ".join(dept_names)
        
        context = {
            'role': 'hr',
            'tenant_name': request.subdomain,
            'username': request.user.username,
            'hr_profile': hr_profile,
            'managed_departments': managed_departments,
            'total_employees': total_employees,
            'pending_requests': pending_requests,
            'present_today': present_today,
            'absent_today': absent_today,
            'on_leave_today': on_leave_today,
            'not_marked_today': not_marked_today,
            'recent_requests': recent_requests,
        }
        
        return render(request, 'accounts/hr/hr_home.html', context)
    except Account.DoesNotExist:
        return HttpResponse("Account not found!")
    except Exception as e:
        print(f"[ERROR] hr_home: {str(e)}")
        import traceback
        traceback.print_exc()
        return HttpResponse(f"Error loading page: {str(e)}")