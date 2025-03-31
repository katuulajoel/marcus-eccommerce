from django.db import models
from apps.products.models import PartOption, Category

class PreConfiguredProduct(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        db_table = 'preconfiguredproduct'
        
    def __str__(self):
        return self.name

class PreConfiguredProductParts(models.Model):
    preconfigured_product = models.ForeignKey(
        PreConfiguredProduct, 
        on_delete=models.CASCADE,
        related_name='parts'
    )
    part_option = models.ForeignKey(PartOption, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'preconfiguredproductparts'
        
    def __str__(self):
        return f"{self.preconfigured_product.name} - {self.part_option.name}"

# Materialized view models
class BestSellingPreconfiguredProduct(models.Model):
    preconfigured_product_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    times_ordered = models.IntegerField()
    
    class Meta:
        db_table = 'bestsellingpreconfiguredproduct'
        managed = False
        
    def __str__(self):
        return f"{self.name} (ordered {self.times_ordered} times)"

class TopPreconfiguredProductsPerCategory(models.Model):
    preconfigured_product_id = models.IntegerField(primary_key=True)
    category_id = models.IntegerField()
    preconfigured_name = models.CharField(max_length=255)
    times_ordered = models.IntegerField()
    
    class Meta:
        db_table = 'toppreconfiguredproductspercategory'
        managed = False
        
    def __str__(self):
        return f"{self.preconfigured_name} (Category {self.category_id})"
