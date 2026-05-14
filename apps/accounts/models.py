from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('staff', 'Staff'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('pending', 'Pending'),
        ('rejected', 'Rejected'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='staff')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

    def is_admin(self):
        return self.role == 'admin'

    def is_staff_member(self):
        return self.role == 'staff'

    def is_active_user(self):
        return self.status == 'active'

    def is_pending(self):
        return self.status == 'pending'