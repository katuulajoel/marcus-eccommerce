from django.db import models

class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='products/images/', null=True, blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Part(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    product = models.ForeignKey(Product, related_name='parts', on_delete=models.CASCADE)
    step_number = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.name} (Step {self.step_number})"

class PartOption(models.Model):
    id = models.AutoField(primary_key=True)
    part = models.ForeignKey(Part, related_name='options', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='parts/options/images/', null=True, blank=True)

    def __str__(self):
        return self.name