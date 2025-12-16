from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import uuid

# Roles
ROLE_CHOICES = (
    ("EMPLOYEE", "Employee"),
    ("HR", "HR"),
)


# Department Model
class Department(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Account(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    is_approved = models.BooleanField(default=True)  # Add this field
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='approved_accounts'
    )
    approved_at = models.DateTimeField(null=True, blank=True) 
    
    def __str__(self):
        return f"{self.user.username} ({self.role})"


# Employee Profile
class EmployeeProfile(models.Model):
    account = models.OneToOneField(Account, on_delete=models.CASCADE)
    total_leaves = models.IntegerField(default=20)
    department = models.ForeignKey(
        Department, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='employees'
    )

    def __str__(self):
        return f"Employee Profile - {self.account.user.username}"


# HR Profile - ADD departments (ManyToMany) and is_admin field
class HRProfile(models.Model):
    account = models.OneToOneField(Account, on_delete=models.CASCADE)
    departments = models.ManyToManyField(
        Department, 
        blank=True,
        related_name='hr_managers',
        help_text="Departments this HR manages. Leave empty for full access."
    )
    is_admin = models.BooleanField(
        default=False,
        help_text="Admin HRs have access to all departments"
    )

    def __str__(self):
        return f"HR Profile - {self.account.user.username}"
    
    def has_access_to_employee(self, employee_profile):
        """Check if this HR can manage the given employee"""
        # Admin HR has access to everyone
        if self.is_admin:
            return True
        
        # If HR has no departments assigned, they have access to all
        if not self.departments.exists():
            return True
        
        # Check if employee's department is in HR's departments
        if employee_profile.department:
            return self.departments.filter(id=employee_profile.department.id).exists()
        
        # If employee has no department, allow access
        return True