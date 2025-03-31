from django.db import models

class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'category'

class Part(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, related_name='parts', on_delete=models.CASCADE, db_column='category_id')

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'part'

class PartOption(models.Model):
    id = models.AutoField(primary_key=True)
    part = models.ForeignKey(Part, related_name='options', on_delete=models.CASCADE, db_column='part_id')
    name = models.CharField(max_length=255)
    default_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'partoption'

class Stock(models.Model):
    id = models.AutoField(primary_key=True)
    part_option = models.ForeignKey(PartOption, related_name='stock', on_delete=models.CASCADE, db_column='part_option_id')
    quantity = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.part_option.name}: {self.quantity}"
    
    class Meta:
        db_table = 'stock'
