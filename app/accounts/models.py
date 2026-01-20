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

    def __str__(self):
        return self.username

