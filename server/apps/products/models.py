from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='categories/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Shipping profile fields
    unit_weight_kg = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0.00,
        help_text="Weight per single item in kilograms"
    )
    unit_length_cm = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0.00,
        help_text="Length per single item in centimeters"
    )
    unit_width_cm = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0.00,
        help_text="Width per single item in centimeters"
    )
    unit_height_cm = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0.00,
        help_text="Height per single item in centimeters"
    )
    stackable = models.BooleanField(
        default=False,
        help_text="Can items be stacked efficiently for delivery?"
    )
    max_boda_quantity = models.IntegerField(
        default=1,
        help_text="Maximum quantity deliverable by boda boda (0 = never use boda)"
    )
    requires_helper = models.BooleanField(
        default=False,
        help_text="Requires delivery assistance or assembly help"
    )
    requires_extra_care = models.BooleanField(
        default=False,
        help_text="Fragile or valuable items requiring extra care"
    )
    shipping_notes = models.TextField(
        blank=True,
        help_text="Special shipping/handling instructions"
    )

    class Meta:
        db_table = 'category'

    def __str__(self):
        return self.name

class Part(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    step = models.IntegerField(default=0)

    class Meta:
        db_table = 'part'

    def __str__(self):
        return self.name

class PartOption(models.Model):
    part = models.ForeignKey(Part, on_delete=models.CASCADE, related_name='options')
    name = models.CharField(max_length=255)
    default_price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='part_options/', null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    minimum_payment_percentage = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        help_text="Minimum upfront payment required (0.00 to 1.00). Example: 0.70 means 70% required upfront"
    )

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
