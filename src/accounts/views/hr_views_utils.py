from django.shortcuts import render, redirect
from django.conf import settings
from accounts.models import Account
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from accounts.models import HRProfile
from attendance.models import AttendanceRequest, Attendance
from django.utils import timezone
from approvals.models import EmployeeApproval
from django.contrib.auth.hashers import check_password
from datetime import date
# View all employees attendance
@login_required
def hr_view_attendance(request):
    if request.subdomain=="localhost" or request.subdomain==settings.MAIN_SUBDOMAIN:
        return HttpResponse("Sorry! You can only access by your enterprise subdomain")
    
    account = Account.objects.get(user=request.user)
    
    if account.role.upper() != "HR":
        return HttpResponse("Access denied!")
    
    from accounts.models import EmployeeProfile, HRProfile
    from attendance.models import Attendance
    
    hr_profile = HRProfile.objects.get(account=account)
    
    # Get date filter from query params
    selected_date = request.GET.get('date', date.today().isoformat())
    
    # Get employees based on HR's department access
    if hr_profile.is_admin or not hr_profile.departments.exists():
        # Admin HR or HR with no departments = see all employees
        employees = EmployeeProfile.objects.select_related('account__user', 'department').all()
    else:
        # Regular HR sees only their department's employees
        hr_departments = hr_profile.departments.all()
        employees = EmployeeProfile.objects.filter(
            department__in=hr_departments
        ).select_related('account__user', 'department')
    
    # Get attendance for selected date
    attendance_records = Attendance.objects.filter(
        date=selected_date
    ).select_related('employee__account__user')
    
    # Create a dict for quick lookup
    attendance_dict = {att.employee_id: att for att in attendance_records}
    
    # Combine employees with their attendance
    employee_attendance = []
    for emp in employees:
        att = attendance_dict.get(emp.id)
        employee_attendance.append({
            'employee': emp,
            'attendance': att,
            'status': att.status if att else 'NOT_MARKED'
        })
    
    context = {
        'role':'hr',
        'employee_attendance': employee_attendance,
        'selected_date': selected_date,
        'hr_profile': hr_profile,
    }
    
    return render(request, 'accounts/hr/hr_view_attendance.html', context)


# Mark attendance - with department check
@login_required
def hr_mark_attendance(request):
    if request.subdomain=="localhost" or request.subdomain==settings.MAIN_SUBDOMAIN:
        return HttpResponse("Sorry! You can only access by your enterprise subdomain")
    
    account = Account.objects.get(user=request.user)
    
    if account.role.upper() != "HR":
        return HttpResponse("Access denied!")
    
    from accounts.models import HRProfile, EmployeeProfile
    from attendance.models import Attendance
    
    hr_profile = HRProfile.objects.get(account=account)
    
    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        date_str = request.POST.get('date')
        status = request.POST.get('status')
        
        employee = EmployeeProfile.objects.get(id=employee_id)
        
        # Check if HR has access to this employee
        if not hr_profile.has_access_to_employee(employee):
            return HttpResponse("Access denied! You don't have permission to mark attendance for this employee.")
        
        # Update or create attendance
        attendance, created = Attendance.objects.update_or_create(
            employee=employee,
            date=date_str,
            defaults={
                'status': status,
                'marked_by': hr_profile
            }
        )
        
        return redirect('hr_view_attendance')
    
    # For GET request, show the form with filtered employees
    if hr_profile.is_admin or not hr_profile.departments.exists():
        employees = EmployeeProfile.objects.select_related('account__user', 'department').all()
    else:
        hr_departments = hr_profile.departments.all()
        employees = EmployeeProfile.objects.filter(
            department__in=hr_departments
        ).select_related('account__user', 'department')
    
    context = {
        'role':'hr',
        'employees': employees,
        'today': date.today().isoformat(),
    }
    
    return render(request, 'accounts/hr/hr_mark_attendance.html', context)


# Review requests - with department filtering
@login_required
def hr_review_requests(request):
    if request.subdomain=="localhost" or request.subdomain==settings.MAIN_SUBDOMAIN:
        return HttpResponse("Sorry! You can only access by your enterprise subdomain")
    
    account = Account.objects.get(user=request.user)
    
    if account.role.upper() != "HR":
        return HttpResponse("Access denied!")
    
    
    
    hr_profile = HRProfile.objects.get(account=account)
    
    # Handle approval/rejection
    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        action = request.POST.get('action')
        
        att_request = AttendanceRequest.objects.select_related('employee').get(id=request_id)
        
        # Check if HR has access to this employee
        if not hr_profile.has_access_to_employee(att_request.employee):
            return HttpResponse("Access denied! You don't have permission to review this request.")
        
        if action == 'approve':
            att_request.status = 'APPROVED'
            att_request.reviewed_by = hr_profile
            att_request.reviewed_at = timezone.now()
            att_request.save()
            
            # Update or create the actual attendance record
            Attendance.objects.update_or_create(
                employee=att_request.employee,
                date=att_request.date,
                defaults={
                    'status': att_request.requested_status,
                    'marked_by': hr_profile
                }
            )
            
        elif action == 'reject':
            att_request.status = 'REJECTED'
            att_request.reviewed_by = hr_profile
            att_request.reviewed_at = timezone.now()
            att_request.save()
        
        return redirect('hr_review_requests')
    
    # Get requests based on HR's department access
    if hr_profile.is_admin or not hr_profile.departments.exists():
        # Admin sees all requests
        pending_requests = AttendanceRequest.objects.filter(
            status='PENDING'
        ).select_related('employee__account__user', 'employee__department').order_by('-created_at')
        
        reviewed_requests = AttendanceRequest.objects.filter(
            status__in=['APPROVED', 'REJECTED']
        ).select_related('employee__account__user', 'employee__department', 'reviewed_by__account__user').order_by('-reviewed_at')[:20]
    else:
        # Regular HR sees only their department's requests
        hr_departments = hr_profile.departments.all()
        
        pending_requests = AttendanceRequest.objects.filter(
            status='PENDING',
            employee__department__in=hr_departments
        ).select_related('employee__account__user', 'employee__department').order_by('-created_at')
        
        reviewed_requests = AttendanceRequest.objects.filter(
            status__in=['APPROVED', 'REJECTED'],
            employee__department__in=hr_departments
        ).select_related('employee__account__user', 'employee__department', 'reviewed_by__account__user').order_by('-reviewed_at')[:20]
    
    context = {
        'role':'hr',
        'pending_requests': pending_requests,
        'reviewed_requests': reviewed_requests,
        'hr_profile': hr_profile,
    }
    
    return render(request, 'accounts/hr/hr_review_requests.html', context)


@login_required
def hr_employee_approval_list(request):
    """HR view to see pending employee applications"""
    if request.subdomain=="localhost" or request.subdomain==settings.MAIN_SUBDOMAIN:
        return HttpResponse("Sorry! You can only access by your enterprise subdomain")
    
    try:
        account = Account.objects.get(user=request.user)
        
        if account.role.upper() != "HR":
            return HttpResponse("Access denied! Only HRs can access this page.")
        
        hr_profile = HRProfile.objects.get(account=account)
        
        # Filter applications based on HR's department access
        if hr_profile.is_admin or not hr_profile.departments.exists():
            # Admin HR sees all applications
            pending_applications = EmployeeApproval.objects.filter(
                status='PENDING'
            ).select_related('department').order_by('-applied_at')
        else:
            # Regular HR sees only their department's applications
            hr_departments = hr_profile.departments.all()
            pending_applications = EmployeeApproval.objects.filter(
                status='PENDING',
                department__in=hr_departments
            ).select_related('department').order_by('-applied_at')
        
        # Get recently reviewed
        if hr_profile.is_admin or not hr_profile.departments.exists():
            reviewed_applications = EmployeeApproval.objects.filter(
                status__in=['APPROVED', 'REJECTED']
            ).select_related('department', 'reviewed_by').order_by('-reviewed_at')[:20]
        else:
            reviewed_applications = EmployeeApproval.objects.filter(
                status__in=['APPROVED', 'REJECTED'],
                department__in=hr_departments
            ).select_related('department', 'reviewed_by').order_by('-reviewed_at')[:20]
        
        context = {
            'tenant_name': request.subdomain,
            'hr_profile': hr_profile,
            'pending_applications': pending_applications,
            'reviewed_applications': reviewed_applications,
        }
        
        return render(request, 'accounts/hr/hr_employee_approval_list.html', context)
        
    except Account.DoesNotExist:
        return HttpResponse("Account not found!")
    except Exception as e:
        print(f"[ERROR] hr_employee_approval_list: {str(e)}")
        import traceback
        traceback.print_exc()
        return HttpResponse(f"Error: {str(e)}")


@login_required
def hr_employee_approval_detail(request, application_id):
    """HR view to approve/reject employee application"""
    if request.subdomain=="localhost" or request.subdomain==settings.MAIN_SUBDOMAIN:
        return HttpResponse("Sorry! You can only access by your enterprise subdomain")
    
    try:
        account = Account.objects.get(user=request.user)
        
        if account.role.upper() != "HR":
            return HttpResponse("Access denied! Only HRs can access this page.")
        
        hr_profile = HRProfile.objects.get(account=account)
        employee_application = EmployeeApproval.objects.get(id=application_id, status='PENDING')
        
        # Check if HR has access to this application's department
        if not hr_profile.is_admin and hr_profile.departments.exists():
            if employee_application.department not in hr_profile.departments.all():
                return HttpResponse("Access denied! You don't manage this department.")
        
        if request.method == 'POST':
            action = request.POST.get('action')
            
            if action == 'approve':
                # CREATE THE ACTUAL USER AND EMPLOYEE ACCOUNT
                user = User.objects.create(
                    username=employee_application.username,
                    email=employee_application.email,
                    first_name=employee_application.first_name,
                    last_name=employee_application.last_name
                )
                
                # Set the hashed password
                user.password = employee_application.password_hash
                user.save()
                
                print(f"[APPROVAL] Employee user created: {user.username}")
                
                # Create Employee account
                emp_account = Account.objects.create(
                    user=user,
                    role='EMPLOYEE'
                )
                
                # Get employee profile (created by signal)
                employee_profile = EmployeeProfile.objects.get(account=emp_account)
                employee_profile.department = employee_application.department
                employee_profile.total_leaves = employee_application.total_leaves
                employee_profile.save()
                
                # Update application status
                employee_application.status = 'APPROVED'
                employee_application.reviewed_by = request.user
                employee_application.reviewed_at = timezone.now()
                employee_application.save()
                
                print(f"[APPROVAL] Employee approved: {user.username}")
                
                # Send approval email
                try:
                    send_mail(
                        subject=f'Employee Application Approved - {request.subdomain}',
                        message=f'''
                            Congratulations {employee_application.first_name}!

                            Your employee application has been APPROVED.

                            ✅ Account Details:
                            - Username: {user.username}
                            - Email: {user.email}
                            - Department: {employee_application.department.name}
                            - Leave Balance: {employee_application.total_leaves} days
                            - Organization: {request.subdomain}

                            🔗 Login here:
                            http://{request.subdomain}.localhost:8000/users/user-login/

                            Welcome to {request.subdomain}!

                            ---
                            {request.subdomain} HR Team
                        ''',
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[user.email],
                        fail_silently=False,
                    )
                    print(f"[EMAIL] Approval email sent to {user.email}")
                except Exception as e:
                    print(f"[ERROR] Failed to send approval email: {e}")
                
                return redirect('hr-employee-approvals')
            
            elif action == 'reject':
                rejection_reason = request.POST.get('rejection_reason', 'Not specified')
                
                # Update application status
                employee_application.status = 'REJECTED'
                employee_application.reviewed_by = request.user
                employee_application.reviewed_at = timezone.now()
                employee_application.rejection_reason = rejection_reason
                employee_application.save()
                
                print(f"[REJECTION] Employee application rejected: {employee_application.username}")
                
                # Send rejection email
                try:
                    send_mail(
                        subject=f'Employee Application Update - {request.subdomain}',
                        message=f'''
                            Dear {employee_application.first_name or employee_application.username},

                            Thank you for your interest in joining {request.subdomain}.

                            After review, we are unable to approve your application at this time.

                            Reason: {rejection_reason}

                            If you have any questions, please contact HR at {request.user.email}.

                            ---
                            {request.subdomain} HR Team
                        ''',
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[employee_application.email],
                        fail_silently=False,
                    )
                    print(f"[EMAIL] Rejection email sent to {employee_application.email}")
                except Exception as e:
                    print(f"[ERROR] Failed to send rejection email: {e}")
                
                # Delete the rejected application
                employee_application.delete()
                
                return redirect('hr-employee-approvals')
        
        context = {
            'tenant_name': request.subdomain,
            'hr_profile': hr_profile,
            'employee_application': employee_application,
        }
        
        return render(request, 'accounts/hr/hr_employee_approval_detail.html', context)
        
    except EmployeeApproval.DoesNotExist:
        return HttpResponse("Employee application not found or already reviewed!")
    except Exception as e:
        print(f"[ERROR] hr_employee_approval_detail: {str(e)}")
        import traceback
        traceback.print_exc()
        return HttpResponse(f"Error: {str(e)}")