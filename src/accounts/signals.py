from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Account, EmployeeProfile, HRProfile

@receiver(post_save, sender=Account)
def create_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == "EMPLOYEE":
            EmployeeProfile.objects.create(account=instance)
        elif instance.role == "HR":
            HRProfile.objects.create(account=instance)

@receiver(post_save, sender=Account)
def save_user_profile(sender, instance, **kwargs):
    """Save the profile when Account is saved"""
    if instance.role == "EMPLOYEE":
        if hasattr(instance, 'employeeprofile'):
            instance.employeeprofile.save()
        else:
            EmployeeProfile.objects.create(account=instance)
    elif instance.role == "HR":
        if hasattr(instance, 'hrprofile'):
            instance.hrprofile.save()
        else:
            HRProfile.objects.create(account=instance)