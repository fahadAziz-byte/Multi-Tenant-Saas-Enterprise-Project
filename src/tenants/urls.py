from django.urls import path
from .tenant_views import hr_approval_list,hr_approval_detail,department_detail
urlpatterns = [
    path('hr-approvals/<str:schema_name>', hr_approval_list, name='hr-approval-list'),
    path('hr-approval/<str:schema_name>/<uuid:application_id>/', hr_approval_detail, name='hr-approval-detail'),
    path('department/<str:schema_name>/<uuid:department_id>/', department_detail, name='department-detail'),
    # path("<str:pk>/", tenant_detail_view),
    # path("<str:pk>/new-user/", tenant_createuser__view),
]



