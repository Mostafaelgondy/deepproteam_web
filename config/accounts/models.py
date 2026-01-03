from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import transaction
from decimal import Decimal

class User(AbstractUser):
    """Custom user model with role management and wallet support"""
    ROLE_CHOICES = (
        ('client', 'Client'),
        ('dealer', 'Dealer'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    email_verified = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)  # For dealers, admin approval
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['is_approved']),
        ]
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class SubscriptionPlan(models.Model):
    """Subscription plans for dealers - EGP based"""
    PLAN_CHOICES = (
        ('starter', 'Starter'),
        ('pro', 'Pro'),
        ('enterprise', 'Enterprise'),
    )
    
    name = models.CharField(max_length=100, choices=PLAN_CHOICES, unique=True)
    price_egp = models.DecimalField(max_digits=10, decimal_places=2)
    max_products = models.PositiveIntegerField()  # 0 = unlimited
    allows_videos = models.BooleanField(default=False)
    ads_enabled = models.BooleanField(default=False)
    duration_days = models.PositiveIntegerField(default=30)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    
    class Meta:
        ordering = ['price_egp']
    
    def __str__(self):
        return f"{self.get_name_display()} - {self.price_egp} EGP"


class DealerProfile(models.Model):
    """Dealer-specific profile with subscription tracking"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='dealer_profile')
    business_name = models.CharField(max_length=255, blank=True)
    business_description = models.TextField(blank=True)
    subscription_plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True, blank=True)
    subscription_start_date = models.DateTimeField(null=True, blank=True)
    subscription_end_date = models.DateTimeField(null=True, blank=True)
    products_published = models.PositiveIntegerField(default=0)
    has_used_free_product = models.BooleanField(default=False)  # Track if free product used
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal('0.00'))
    total_sales = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def is_subscription_active(self):
        """Check if current subscription is valid"""
        if not self.subscription_end_date:
            return False
        from django.utils import timezone
        return timezone.now() <= self.subscription_end_date
    
    def get_active_product_count(self):
        """Get count of active published products"""
        from config.products.models import Product
        return Product.objects.filter(
            dealer=self.user,
            status='approved'
        ).count()
    
    def can_publish_product(self):
        """Check if dealer can publish a new product"""
        # First product is always free
        if not self.has_used_free_product:
            return True, "Free first product available"
        
        # After first product, need active subscription
        if not self.subscription_plan:
            return False, "Subscription required"
        
        if not self.is_subscription_active():
            return False, "Subscription expired"
        
        active_count = self.get_active_product_count()
        if self.subscription_plan.max_products > 0:
            if active_count >= self.subscription_plan.max_products:
                return False, f"Max products ({self.subscription_plan.max_products}) reached"
        
        return True, "Can publish"
    
    def __str__(self):
        return f"Dealer: {self.user.username}"


class EGPWallet(models.Model):
    """Egyptian Pound wallet"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='egp_wallet')
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.balance:.2f} EGP"


class GoldWallet(models.Model):
    """Gold wallet (premium credit)"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='gold_wallet')
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.balance:.2f} Gold"


class MassWallet(models.Model):
    """Mass wallet (regular credit)"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='mass_wallet')
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.balance:.2f} Mass"
