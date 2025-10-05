from django.db import models
from django.core.validators import RegexValidator
from decimal import Decimal
from apps.customers.models import Customer
from apps.preconfigured_products.models import PreConfiguredProduct


class ShippingAddress(models.Model):
    """Shipping address for an order - allows different addresses per order"""
    id = models.AutoField(primary_key=True)
    recipient_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, validators=[
        RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    ])
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100)
    state_province = models.CharField(max_length=100, null=True, blank=True)
    postal_code = models.CharField(max_length=20, null=True, blank=True)
    country = models.CharField(max_length=100, default='Uganda')

    def __str__(self):
        return f"{self.recipient_name} - {self.address_line1}, {self.city}"

    class Meta:
        db_table = 'shippingaddress'
        verbose_name = 'Shipping Address'
        verbose_name_plural = 'Shipping Addresses'


class Orders(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('partial', 'Partial'),
        ('completed', 'Completed'),
    ]

    FULFILLMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_production', 'In Production'),
        ('ready_for_pickup', 'Ready for Pickup'),
        ('in_delivery', 'In Delivery'),
        ('delivered', 'Delivered'),
    ]

    id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, related_name='orders', on_delete=models.CASCADE, db_column='customer_id')
    shipping_address = models.ForeignKey(ShippingAddress, related_name='orders', on_delete=models.PROTECT, db_column='shipping_address_id', null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_required_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    fulfillment_status = models.CharField(max_length=20, choices=FULFILLMENT_STATUS_CHOICES, default='pending')
    is_fulfillable = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} by {self.customer}"

    def calculate_minimum_required_amount(self):
        """Calculate minimum required payment based on part option percentages"""
        total_minimum = 0
        for order_product in self.products.all():
            for item in order_product.items.all():
                total_minimum += item.minimum_payment_required
        return total_minimum

    def update_payment_status(self):
        """Update payment status and fulfillable flag based on amount paid"""
        if self.amount_paid >= self.total_price:
            self.payment_status = 'completed'
            self.is_fulfillable = True
        elif self.amount_paid >= self.minimum_required_amount:
            self.payment_status = 'partial'
            self.is_fulfillable = True
        else:
            self.payment_status = 'pending'
            self.is_fulfillable = False
        self.save()

    @property
    def balance_due(self):
        """Calculate remaining balance"""
        from decimal import Decimal
        return max(Decimal('0'), self.total_price - self.amount_paid)

    class Meta:
        db_table = 'orders'
        verbose_name_plural = 'Orders'

class OrderProduct(models.Model):
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Orders, related_name='products', on_delete=models.CASCADE, db_column='order_id')
    preconfigured_product = models.ForeignKey(PreConfiguredProduct, related_name='order_products', 
                                             on_delete=models.CASCADE, db_column='preconfigured_product_id', null=True)
    custom_name = models.CharField(max_length=255, null=True, blank=True)
    base_product_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.base_product_name} in Order {self.order.id}"
    
    class Meta:
        db_table = 'orderproduct'

class OrderItem(models.Model):
    id = models.AutoField(primary_key=True)
    order_product = models.ForeignKey(OrderProduct, related_name='items', on_delete=models.CASCADE, db_column='order_product_id')
    part_name = models.CharField(max_length=255)
    option_name = models.CharField(max_length=255)
    final_price = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_payment_required = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    def __str__(self):
        return f"{self.part_name}: {self.option_name}"

    class Meta:
        db_table = 'orderitem'


class Payment(models.Model):
    PAID_BY_CHOICES = [
        ('customer', 'Customer'),
        ('delivery_person', 'Delivery Person'),
    ]

    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Orders, related_name='payments', on_delete=models.CASCADE, db_column='order_id')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=100)
    payment_date = models.DateTimeField(auto_now_add=True)
    paid_by = models.CharField(max_length=20, choices=PAID_BY_CHOICES, default='customer')
    transaction_reference = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Payment {self.id} for Order {self.order.id} - ${self.amount}"

    def save(self, *args, **kwargs):
        """Override save to update order payment status"""
        super().save(*args, **kwargs)
        # Update order's total paid amount
        self.order.amount_paid = sum(p.amount for p in self.order.payments.all())
        self.order.update_payment_status()

    class Meta:
        db_table = 'payment'
        ordering = ['-payment_date']