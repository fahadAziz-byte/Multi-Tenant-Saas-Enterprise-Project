from django.db import models
from django.conf import settings
from django.contrib.auth.hashers import make_password
from accounts.models import Department
import uuid

# =============================================
# APPROVAL STATUS CHOICES
# =============================================
STATUS_CHOICES = (
    ("PENDING", "Pending"),
    ("APPROVED", "Approved"),
    ("REJECTED", "Rejected"),
)


# =============================================
# HR APPROVAL MODEL
# =============================================
class HRApproval(models.Model):
    """HR signup requests that need tenant owner approval"""
    
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    
    # User credentials (stored temporarily)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=255)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    
    # HR-specific fields
    is_admin = models.BooleanField(
        default=False,
        help_text="Admin HRs have access to all departments"
    )
    requested_departments = models.ManyToManyField(
        Department,
        blank=True,
        related_name='hr_approval_requests',
        help_text="Departments this HR wants to manage"
    )
    
    # Approval tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )
    
    # Timestamps
    applied_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    # Reviewer info
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_hr_approvals'
    )
    rejection_reason = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-applied_at']
        verbose_name = "HR Approval Request"
        verbose_name_plural = "HR Approval Requests"
    
    def __str__(self):
        return f"{self.username} - {self.status}"


# =============================================
# EMPLOYEE APPROVAL MODEL
# =============================================
class EmployeeApproval(models.Model):
    """Employee signup requests that need HR approval"""
    
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    
    # User credentials (stored temporarily)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=255)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    
    # Employee-specific fields
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='employee_approval_requests'
    )
    total_leaves = models.IntegerField(
        default=20,
        help_text="Initial leave balance"
    )
    
    # Approval tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )
    
    # Timestamps
    applied_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    # Reviewer info (HR who approved/rejected)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_employee_approvals'
    )
    rejection_reason = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-applied_at']
        verbose_name = "Employee Approval Request"
        verbose_name_plural = "Employee Approval Requests"
    
    def __str__(self):
        return f"{self.username} ({self.department.name}) - {self.status}"