from django.db import models
from django.utils import timezone
from accounts.models import EmployeeProfile, HRProfile
import uuid

STATUS_CHOICES = (
    ("PRESENT", "Present"),
    ("ABSENT", "Absent"),
    ("LEAVE", "Leave"),
)

class Attendance(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    marked_by = models.ForeignKey(HRProfile, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)  # Add default
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("employee", "date")
        ordering = ['-date']

    def __str__(self):
        return f"{self.employee.account.user.username} - {self.date} - {self.status}"


class AttendanceRequest(models.Model):
    """Employees can request attendance corrections"""
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE)
    date = models.DateField()
    requested_status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=(
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
    ), default="PENDING")
    reviewed_by = models.ForeignKey(HRProfile, on_delete=models.SET_NULL, null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)  # Add default

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee.account.user.username} - {self.date} - {self.status}"