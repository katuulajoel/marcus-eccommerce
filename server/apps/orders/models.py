from django.db import models
from server.apps.customers.models import Customer

class Order(models.Model):
    id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, related_name='orders', on_delete=models.SET_NULL, null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id}"

class OrderProduct(models.Model):
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, related_name='order_products', on_delete=models.CASCADE)
    preconfigured_product_id = models.IntegerField(null=True, blank=True)
    custom_name = models.CharField(max_length=255, null=True, blank=True)
    base_product_name = models.CharField(max_length=255)

    def __str__(self):
        return f"OrderProduct #{self.id} for Order #{self.order.id}"