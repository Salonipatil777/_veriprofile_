# signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import HRUser, AdminNotification
from django.contrib.auth.models import User

@receiver(post_save, sender=HRUser)
def send_hr_notification(sender, instance, created, **kwargs):
    if created:
        # Create a notification for the admin
        admin_user = User.objects.get(is_superuser=True)  # Replace with how you identify the admin user
        message = f'New HR Added: {instance.username}'
        AdminNotification.objects.create(user=admin_user, message=message)
