from django.db import models
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='customer_profile')
    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=100, null=True, blank=True)
    password_reset_token = models.CharField(max_length=100, null=True, blank=True)
    password_reset_token_expires = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name or self.email or self.phone or f"Customer {self.id}"

    def generate_verification_token(self):
        """Generate a unique email verification token"""
        self.email_verification_token = get_random_string(64)
        self.save()
        return self.email_verification_token

    def generate_password_reset_token(self):
        """Generate a unique password reset token with 1-hour expiry"""
        from django.utils import timezone
        from datetime import timedelta

        self.password_reset_token = get_random_string(64)
        self.password_reset_token_expires = timezone.now() + timedelta(hours=1)
        self.save()
        return self.password_reset_token

    class Meta:
        db_table = 'customer'