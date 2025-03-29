from django.db import models
from apps.customers.models import Customer
from apps.preconfigured_products.models import PreConfiguredProduct

class Orders(models.Model):
    id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, related_name='orders', on_delete=models.CASCADE, db_column='customer_id')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} by {self.customer}"
    
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

    def __str__(self):
        return f"{self.part_name}: {self.option_name}"
    
    class Meta:
        db_table = 'orderitem'