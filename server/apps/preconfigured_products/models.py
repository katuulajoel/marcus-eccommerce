from django.db import models
from apps.products.models import Product, PartOption

class PreConfiguredProduct(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, related_name='preconfigured_products', on_delete=models.CASCADE, db_column='product_id')
    name = models.CharField(max_length=255)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'preconfiguredproduct'

class PreConfiguredProductParts(models.Model):
    id = models.AutoField(primary_key=True)
    preconfigured_product = models.ForeignKey(PreConfiguredProduct, related_name='parts', 
                                             on_delete=models.CASCADE, db_column='preconfigured_product_id')
    part_option = models.ForeignKey(PartOption, related_name='preconfigured_products', 
                                   on_delete=models.CASCADE, db_column='part_option_id')

    def __str__(self):
        return f"{self.preconfigured_product.name} - {self.part_option.name}"
    
    class Meta:
        db_table = 'preconfiguredproductparts'
