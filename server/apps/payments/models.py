from django.db import models
from apps.orders.models import Orders, Payment


class PaymentGatewayConfig(models.Model):
    """Store payment gateway configurations"""
    GATEWAY_CHOICES = [
        ('stripe', 'Stripe'),
        ('mtn_momo', 'MTN Mobile Money'),
        ('airtel_money', 'Airtel Money'),
    ]

    gateway_name = models.CharField(max_length=50, choices=GATEWAY_CHOICES, unique=True)
    is_active = models.BooleanField(default=True)
    api_key = models.CharField(max_length=255, blank=True)
    api_secret = models.CharField(max_length=255, blank=True)
    environment = models.CharField(max_length=20, default='sandbox')  # sandbox or production
    webhook_secret = models.CharField(max_length=255, blank=True)
    additional_config = models.JSONField(default=dict, blank=True)  # For gateway-specific configs
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_gateway_name_display()} ({self.environment})"

    class Meta:
        db_table = 'payment_gateway_config'


class PaymentTransaction(models.Model):
    """Track all payment transaction attempts and status"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('requires_action', 'Requires Action'),  # For 2FA, phone verification etc
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    GATEWAY_CHOICES = [
        ('stripe', 'Stripe'),
        ('mtn_momo', 'MTN Mobile Money'),
        ('airtel_money', 'Airtel Money'),
    ]

    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Orders, related_name='payment_transactions', on_delete=models.CASCADE, db_column='order_id')
    payment = models.OneToOneField(Payment, related_name='transaction', on_delete=models.SET_NULL, null=True, blank=True, db_column='payment_id')

    gateway = models.CharField(max_length=50, choices=GATEWAY_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Gateway-specific identifiers
    gateway_transaction_id = models.CharField(max_length=255, null=True, blank=True)  # Stripe payment intent, MTN reference, etc
    gateway_reference = models.CharField(max_length=255, null=True, blank=True)  # Additional reference from gateway

    # Customer payment details (for mobile money)
    customer_phone = models.CharField(max_length=20, null=True, blank=True)
    customer_email = models.EmailField(null=True, blank=True)

    # Response data from gateway
    gateway_response = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(null=True, blank=True)

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.gateway} - {self.amount} {self.currency} - {self.status}"

    class Meta:
        db_table = 'payment_transaction'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['gateway_transaction_id']),
            models.Index(fields=['status']),
        ]
