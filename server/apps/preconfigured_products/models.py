from django.db import models
from apps.products.models import Category, PartOption

class PreConfiguredProduct(models.Model):
    id = models.AutoField(primary_key=True)
    category = models.ForeignKey(Category, related_name='preconfigured_products', on_delete=models.CASCADE, db_column='category_id')
    name = models.CharField(max_length=255)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name
    
    class Meta:
        managed = False

class PreConfiguredProductParts(models.Model):
    id = models.AutoField(primary_key=True)
    preconfigured_product = models.ForeignKey(PreConfiguredProduct, related_name='parts', 
                                             on_delete=models.CASCADE, db_column='preconfigured_product_id')
    part_option = models.ForeignKey(PartOption, related_name='preconfigured_products', 
                                   on_delete=models.CASCADE, db_column='part_option_id')

    def __str__(self):
        return f"{self.preconfigured_product.name} - {self.part_option.name}"
    
    class Meta:
        managed = False
        db_table = 'preconfiguredproductparts'

class BestSellingPreconfiguredProduct(models.Model):
    """
    Model representing the BestSellingPreconfiguredProduct materialized view
    """
    preconfigured_product_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    times_ordered = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'bestsellingpreconfiguredproduct'

class TopPreconfiguredProductsPerCategory(models.Model):
    """
    Model representing the TopPreconfiguredProductsPerCategory materialized view
    """
    id = models.AutoField(primary_key=True)
    category_id = models.IntegerField()
    product_name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image_url = models.URLField(null=True, blank=True)
    times_ordered = models.IntegerField(default=0)
    preconfigured_product_id = models.IntegerField()
    
    class Meta:
        managed = False
        db_table = 'toppreconfiguredproductspercategory'
