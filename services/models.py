from django.db import models


class ServiceCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=50, blank=True, null=True)  # For storing icon class names
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Service Category"
        verbose_name_plural = "Service Categories"


class Service(models.Model):
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.category.name} - {self.name}"

    class Meta:
        verbose_name = "Service"
        verbose_name_plural = "Services"


class ServiceVariant(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='variants')
    name = models.CharField(max_length=100)  # e.g., "Kids", "Silk", "Cotton"
    price_modifier = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.service.name} - {self.name}"

    @property
    def final_price(self):
        return self.service.base_price + self.price_modifier

    class Meta:
        verbose_name = "Service Variant"
        verbose_name_plural = "Service Variants"


class PricingRule(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='pricing_rules')
    variant = models.ForeignKey(ServiceVariant, on_delete=models.CASCADE, related_name='pricing_rules', blank=True, null=True)
    min_quantity = models.PositiveIntegerField(default=1)
    max_quantity = models.PositiveIntegerField(blank=True, null=True)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.variant:
            return f"{self.service.name} - {self.variant.name} ({self.min_quantity}-{self.max_quantity or '∞'})"
        return f"{self.service.name} ({self.min_quantity}-{self.max_quantity or '∞'})"

    class Meta:
        verbose_name = "Pricing Rule"
        verbose_name_plural = "Pricing Rules"
