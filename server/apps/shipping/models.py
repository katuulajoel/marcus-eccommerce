from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class ShippingConstants(models.Model):
    """
    System-wide shipping configuration and limits.
    Singleton pattern - only one record should exist.
    """
    # Boda boda limits
    boda_max_weight_kg = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('15.00'),
        help_text="Maximum weight (kg) for boda boda delivery"
    )
    boda_max_length_cm = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal('60.00'),
        help_text="Maximum length (cm) for boda boda delivery"
    )
    boda_max_width_cm = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal('40.00'),
        help_text="Maximum width (cm) for boda boda delivery"
    )
    boda_max_height_cm = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal('40.00'),
        help_text="Maximum height (cm) for boda boda delivery"
    )

    # Van/Pickup limits
    van_max_weight_kg = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal('500.00'),
        help_text="Maximum weight (kg) for van/pickup delivery"
    )
    van_max_length_cm = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal('200.00')
    )
    van_max_width_cm = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal('150.00')
    )
    van_max_height_cm = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal('150.00')
    )

    # Truck limits
    truck_max_weight_kg = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=Decimal('2000.00'),
        help_text="Maximum weight (kg) for truck delivery"
    )

    # Additional fees (in UGX)
    helper_fee_ugx = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('15000.00'),
        help_text="Fee for delivery helper/assembly assistance"
    )
    extra_care_fee_ugx = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('5000.00'),
        help_text="Fee for fragile/valuable item handling"
    )

    class Meta:
        db_table = 'shipping_constants'
        verbose_name = 'Shipping Constants'
        verbose_name_plural = 'Shipping Constants'

    def __str__(self):
        return "Shipping Configuration"

    def save(self, *args, **kwargs):
        """Enforce singleton pattern"""
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_instance(cls):
        """Get or create the singleton instance"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class ShippingZone(models.Model):
    """
    Delivery zones (e.g., Kampala Central, Inner Kampala, etc.)
    """
    zone_code = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique zone code (e.g., KLA-1, KLA-2)"
    )
    zone_name = models.CharField(
        max_length=100,
        help_text="Display name (e.g., Kampala Central)"
    )
    distance_range_min_km = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Minimum distance from origin (km)"
    )
    distance_range_max_km = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Maximum distance from origin (km)"
    )
    standard_delivery_days = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Estimated delivery days for standard shipping"
    )
    express_delivery_days = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Estimated delivery days for express shipping (0 = same day)"
    )
    description = models.TextField(
        blank=True,
        help_text="Additional zone information"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this zone is currently serviced"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'shipping_zone'
        ordering = ['distance_range_min_km']
        verbose_name = 'Shipping Zone'
        verbose_name_plural = 'Shipping Zones'

    def __str__(self):
        return f"{self.zone_name} ({self.zone_code})"


class ZoneArea(models.Model):
    """
    Specific areas, neighborhoods, or landmarks within a shipping zone
    """
    zone = models.ForeignKey(
        ShippingZone,
        on_delete=models.CASCADE,
        related_name='areas',
        db_column='zone_id'
    )
    area_name = models.CharField(
        max_length=100,
        help_text="Area, neighborhood, or landmark name"
    )
    keywords = models.JSONField(
        default=list,
        blank=True,
        help_text="Alternative spellings or search keywords for matching"
    )
    is_landmark = models.BooleanField(
        default=False,
        help_text="Is this a major landmark vs a neighborhood?"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'zone_area'
        ordering = ['area_name']
        unique_together = ['zone', 'area_name']
        verbose_name = 'Zone Area'
        verbose_name_plural = 'Zone Areas'

    def __str__(self):
        return f"{self.area_name} ({self.zone.zone_code})"


class ShippingRate(models.Model):
    """
    Shipping rates per zone, delivery method, and service level
    """
    DELIVERY_METHOD_CHOICES = [
        ('boda', 'Boda Boda'),
        ('van', 'Van/Pickup'),
        ('truck', 'Truck'),
    ]

    SERVICE_LEVEL_CHOICES = [
        ('standard', 'Standard'),
        ('express', 'Express'),
    ]

    zone = models.ForeignKey(
        ShippingZone,
        on_delete=models.CASCADE,
        related_name='rates',
        db_column='zone_id'
    )
    delivery_method = models.CharField(
        max_length=20,
        choices=DELIVERY_METHOD_CHOICES
    )
    service_level = models.CharField(
        max_length=20,
        choices=SERVICE_LEVEL_CHOICES
    )
    base_price_ugx = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Base delivery fee in UGX"
    )
    per_km_price_ugx = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Additional per-kilometer charge (mainly for van/truck)"
    )
    min_delivery_hours = models.IntegerField(
        null=True,
        blank=True,
        help_text="Minimum delivery time in hours"
    )
    max_delivery_hours = models.IntegerField(
        null=True,
        blank=True,
        help_text="Maximum delivery time in hours"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this rate is currently offered"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'shipping_rate'
        unique_together = ['zone', 'delivery_method', 'service_level']
        ordering = ['zone', 'delivery_method', 'service_level']
        verbose_name = 'Shipping Rate'
        verbose_name_plural = 'Shipping Rates'

    def __str__(self):
        return f"{self.zone.zone_code} - {self.get_delivery_method_display()} ({self.get_service_level_display()}) - UGX {self.base_price_ugx}"


class OrderShippingMethod(models.Model):
    """
    Tracks shipping method and costs for each order
    """
    DELIVERY_METHOD_CHOICES = [
        ('boda', 'Boda Boda'),
        ('van', 'Van/Pickup'),
        ('truck', 'Truck'),
    ]

    order = models.OneToOneField(
        'orders.Orders',
        on_delete=models.CASCADE,
        related_name='shipping_details',
        db_column='order_id'
    )
    zone = models.ForeignKey(
        ShippingZone,
        on_delete=models.PROTECT,
        related_name='order_shipments',
        db_column='zone_id'
    )
    rate = models.ForeignKey(
        ShippingRate,
        on_delete=models.PROTECT,
        related_name='order_shipments',
        db_column='rate_id',
        null=True,
        blank=True
    )
    delivery_method = models.CharField(
        max_length=20,
        choices=DELIVERY_METHOD_CHOICES
    )
    service_level = models.CharField(
        max_length=20,
        choices=ShippingRate.SERVICE_LEVEL_CHOICES
    )
    base_shipping_cost_ugx = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Base shipping cost before additional fees"
    )
    helper_fee_ugx = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Helper/assembly fee if applicable"
    )
    extra_care_fee_ugx = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Extra care fee if applicable"
    )
    total_shipping_cost_ugx = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Total shipping cost (base + helper + extra care)"
    )
    total_weight_kg = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text="Total weight of shipment"
    )
    total_volume_m3 = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        help_text="Total volume of shipment in cubic meters"
    )
    calculation_notes = models.JSONField(
        default=dict,
        blank=True,
        help_text="Details about how shipping method was determined"
    )
    estimated_delivery_date = models.DateField(
        null=True,
        blank=True,
        help_text="Estimated delivery date"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'order_shipping_method'
        verbose_name = 'Order Shipping Method'
        verbose_name_plural = 'Order Shipping Methods'

    def __str__(self):
        return f"Order #{self.order.id} - {self.get_delivery_method_display()} to {self.zone.zone_name}"

    def save(self, *args, **kwargs):
        """Calculate total shipping cost before saving"""
        self.total_shipping_cost_ugx = (
            self.base_shipping_cost_ugx +
            self.helper_fee_ugx +
            self.extra_care_fee_ugx
        )
        super().save(*args, **kwargs)
