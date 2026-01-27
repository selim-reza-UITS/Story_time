import random
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Base User model to distinguish between roles.
    Using email as the primary login field is recommended for modern platforms.
    """
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)
    is_admin_user = models.BooleanField(default=False)
    #
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)

    def generate_otp(self):
        self.otp = str(random.randint(100000, 999999))
        self.otp_created_at = timezone.now()
        self.save()

    def is_otp_valid(self):
        if self.otp_created_at:
            return timezone.now() < self.otp_created_at + timedelta(minutes=10)
        return False

    def __str__(self):
        return f"{self.username} - {self.is_student} - {self.is_teacher}"

