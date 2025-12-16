# accounts/urls.py
from django.urls import path,include
from .views.views import TenantLoginView,TenantSignupView,user_logout
from .views.emp_views_utils import request_attendance_correction
from .views.hr_views_utils import hr_mark_attendance,hr_view_attendance,hr_review_requests,hr_employee_approval_list, hr_employee_approval_detail
from .views.home_views import employee_home, hr_home
from tenants.tenant_views import tenant_home,tenant_selection
urlpatterns = [
    path('user-login/', TenantLoginView.as_view(), name='loginn'),
    path('user-signup/', TenantSignupView.as_view(), name='signupp'),
    # Redirecting tenant homepage to tenant urls
    path('tenant_homepage/<str:schema_name>', tenant_home,name='tenant-home'),
    path('tenant_selection/',tenant_selection,name='tenant-selection'),
    # Employe URLS
    path('employee/home/', employee_home, name='employee_home'),
    path('request-attendance/', request_attendance_correction, name='request_attendance'),
    
    # hr URls
    path('hr/home/', hr_home, name='hr_home'),
    path('hr/view_attendance/', hr_view_attendance, name='hr_view_attendance'),
    path('hr/mark_attendance/', hr_mark_attendance, name='hr_mark_attendance'),
    path('hr/review_requests/', hr_review_requests, name='hr_review_requests'),
    path('hr/employee-approvals/', hr_employee_approval_list, name='hr-employee-approvals'),
    path('hr/employee-approval/<uuid:application_id>/', hr_employee_approval_detail, name='hr-employee-approval-detail'),
    path('logout/', user_logout, name='logout'),
]
