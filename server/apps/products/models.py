from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'category'

    def __str__(self):
        return self.name

class Part(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        db_table = 'part'

    def __str__(self):
        return self.name

class PartOption(models.Model):
    part = models.ForeignKey(Part, on_delete=models.CASCADE, related_name='options')
    name = models.CharField(max_length=255)
    default_price = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'partoption'

    def __str__(self):
        return f"{self.part.name} - {self.name}"

class Stock(models.Model):
    id = models.AutoField(primary_key=True)
    part_option = models.ForeignKey(PartOption, related_name='stock', on_delete=models.CASCADE, db_column='part_option_id')
    quantity = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.part_option.name}: {self.quantity}"

    class Meta:
        db_table = 'stock'
