from django.conf import settings
from django.core.mail import send_mail


def send_welcome_email(user, password, role):
    subject = f"Welcome to the Platform - Your {role} Account"
    message = (
        f"Hello {user.first_name or user.username},\n\n"
        f"An admin has created a {role} account for you.\n"
        f"Email: {user.email}\n"
        f"Password: {password}\n\n"
        f"Please log in and change your password immediately."
    )
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )