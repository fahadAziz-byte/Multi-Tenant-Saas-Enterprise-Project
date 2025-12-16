from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import HRApproval, EmployeeApproval


# =============================================
# AUTO-DELETE REJECTED APPLICATIONS
# =============================================

@receiver(post_save, sender=HRApproval)
def delete_rejected_hr_approval(sender, instance, **kwargs):
    """Auto-delete rejected HR applications after email is sent"""
    if instance.status == 'REJECTED' and instance.reviewed_at:
        # Send rejection email first
        try:
            send_mail(
                subject=f'HR Application Update',
                message=f'''
Thank you for your interest in joining our organization as an HR.

Unfortunately, we are unable to approve your application at this time.

{f"Reason: {instance.rejection_reason}" if instance.rejection_reason else ""}

If you have any questions, please contact the organization administrator.

Best regards,
Administration Team
                ''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.email],
                fail_silently=True,
            )
            print(f"[EMAIL] Rejection email sent to {instance.email}")
        except Exception as e:
            print(f"[ERROR] Failed to send rejection email: {e}")
        
        # Delete the application after a short delay
        # You can use Celery for this, or just delete immediately
        # For now, we'll keep it for audit trail - you can uncomment to auto-delete
        # instance.delete()


@receiver(post_save, sender=EmployeeApproval)
def delete_rejected_employee_approval(sender, instance, **kwargs):
    """Auto-delete rejected Employee applications after email is sent"""
    if instance.status == 'REJECTED' and instance.reviewed_at:
        # Send rejection email first
        try:
            send_mail(
                subject=f'Employee Application Update',
                message=f'''
Thank you for your interest in joining our organization.

Unfortunately, we are unable to approve your application at this time.

{f"Reason: {instance.rejection_reason}" if instance.rejection_reason else ""}

If you have any questions, please contact your HR department.

Best regards,
HR Team
                ''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.email],
                fail_silently=True,
            )
            print(f"[EMAIL] Rejection email sent to {instance.email}")
        except Exception as e:
            print(f"[ERROR] Failed to send rejection email: {e}")
        
        # Delete after email - uncomment to enable auto-delete
        # instance.delete()