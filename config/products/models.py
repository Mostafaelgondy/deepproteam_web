from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from decimal import Decimal

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Categories'
        indexes = [
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.name


class Product(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('suspended', 'Suspended'),
    )
    
    PAYMENT_TYPE_CHOICES = (
        ('egp', 'Egyptian Pound'),
        ('gold', 'Gold'),
        ('mass', 'Mass'),
    )
    
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    dealer = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    
    # Pricing support for all three currencies
    price_egp = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    price_gold = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    price_mass = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # At least one price must be set
    primary_payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES, default='egp')
    
    stock = models.PositiveIntegerField(default=1)
    image = models.ImageField(upload_to='products/')
    video = models.FileField(upload_to='product_videos/', blank=True, null=True)  # Videos only for Pro/Enterprise
    
    # Moderation
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    rejection_reason = models.TextField(blank=True, null=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_products'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    # Visibility and listing
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    listing_duration_days = models.PositiveIntegerField(default=30)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    publish_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['dealer', 'status']),
            models.Index(fields=['status']),
            models.Index(fields=['category']),
        ]
    
    def clean(self):
        """Validate at least one price is set"""
        if not any([self.price_egp, self.price_gold, self.price_mass]):
            raise ValidationError("At least one price (EGP, Gold, or Mass) must be set")
        if self.price_egp and self.price_egp < 0:
            raise ValidationError("EGP price cannot be negative")
        if self.price_gold and self.price_gold < 0:
            raise ValidationError("Gold price cannot be negative")
        if self.price_mass and self.price_mass < 0:
            raise ValidationError("Mass price cannot be negative")
    
    def get_price(self, currency_type='egp'):
        """Get price for specific currency"""
        if currency_type == 'egp':
            return self.price_egp
        elif currency_type == 'gold':
            return self.price_gold
        elif currency_type == 'mass':
            return self.price_mass
        return self.price_egp  # Default to EGP
    
    def is_published(self):
        """Check if product is published and approved"""
        return self.status == 'approved' and self.is_active
    
    def __str__(self):
        return f"{self.name} - {self.get_status_display()}"


class ProductImage(models.Model):
    """Additional product images"""
    product = models.ForeignKey(Product, related_name='additional_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/')
    alt_text = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Image for {self.product.name}"


class ProductReview(models.Model):
    """Product reviews"""
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    title = models.CharField(max_length=200)
    comment = models.TextField()
    is_verified_purchase = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ('product', 'user')
    
    def __str__(self):
        return f"Review by {self.user.username} for {self.product.name}"
