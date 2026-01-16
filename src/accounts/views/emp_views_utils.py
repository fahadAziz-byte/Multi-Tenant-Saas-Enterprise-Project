from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from helpers.db.schemas import use_tenant_schema_for_auth
from tenants.models import Tenants
from accounts.models import Account
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .views import get_tenant_from_subdomain
from datetime import date
from django.conf import settings
# ============================
# Request from employee to correct his/her attendance 
# ============================
    

def request_attendance_correction(request):
    from datetime import date
    
    host = request.get_host().split(':')[0]
    subdomain = host.split('.')[0]
    if request.subdomain in ["localhost", settings.MAIN_SUBDOMAIN]:
        return HttpResponse("Sorry! You can only access by your enterprise subdomain")
    print("printing before creating account the request.user : ",request.user)
    account = Account.objects.get(user=request.user)
    if not account:
        return HttpResponse("You are not our user to access this page")
    if account.role.upper() != "EMPLOYEE":
        return HttpResponse("You are not authorized as an Employee to access this page")
    
    from accounts.models import EmployeeProfile
    from attendance.models import AttendanceRequest
    
    employee_profile = EmployeeProfile.objects.get(account=account)
    
    if request.method == 'POST':
        date_str = request.POST.get('date')
        requested_status = request.POST.get('status')
        reason = request.POST.get('reason')
        
        AttendanceRequest.objects.create(
            employee=employee_profile,
            date=date_str,
            requested_status=requested_status,
            reason=reason
        )
        
        return redirect('employee_home')
    
    # Get pending requests
    pending_requests = AttendanceRequest.objects.filter(
        employee=employee_profile
    ).order_by('-created_at')[:10]
    
    context = {
        'role':'employee',
        'today': date.today().isoformat(),
        'pending_requests': pending_requests
    }
    
    return render(request, 'accounts/emp/request_attendance.html', context)
