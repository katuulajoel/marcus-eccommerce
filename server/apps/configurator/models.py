# Configurator models based on provided schema

from django.db import models
from server.apps.products.models import PartOption

class PriceAdjustmentRule(models.Model):
    id = models.AutoField(primary_key=True)
    affected_option = models.ForeignKey(PartOption, related_name='price_adjustments', on_delete=models.CASCADE)
    condition_option = models.ForeignKey(PartOption, related_name='conditioned_adjustments', on_delete=models.CASCADE)
    adjusted_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Adjustment for {self.affected_option.name} based on {self.condition_option.name}"

class IncompatibilityRule(models.Model):
    id = models.AutoField(primary_key=True)
    part_option = models.ForeignKey(PartOption, related_name='incompatibilities', on_delete=models.CASCADE)
    incompatible_with_option = models.ForeignKey(PartOption, related_name='incompatible_with', on_delete=models.CASCADE)
    message = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.part_option.name} incompatible with {self.incompatible_with_option.name}"