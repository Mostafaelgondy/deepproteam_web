from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from decimal import Decimal
from config.products.models import Category, Product

class Transaction(models.Model):
    """Transaction model for tracking all wallet movements"""
    TYPE_CHOICES = (
        ('purchase', 'Purchase'),
        ('refund', 'Refund'),
        ('conversion', 'Conversion'),
        ('subscription', 'Subscription Fee'),
        ('admin_adjustment', 'Admin Adjustment'),
    )
    
    CURRENCY_CHOICES = (
        ('egp', 'Egyptian Pound'),
        ('gold', 'Gold'),
        ('mass', 'Mass'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('reversed', 'Reversed'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='transactions', on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=32, choices=TYPE_CHOICES)
    currency = models.CharField(max_length=20, choices=CURRENCY_CHOICES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
    
    # Relations
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions'
    )
    
    # Description for admin/user
    description = models.CharField(max_length=255)
    # Use JSONField where supported; fallback to TextField for SQLite environments
    from django.conf import settings as _settings
    if 'sqlite' in _settings.DATABASES.get('default', {}).get('ENGINE', ''):
        metadata = models.TextField(default='{}', blank=True)
    else:
        metadata = models.JSONField(default=dict, blank=True)  # Store additional data like exchange rates
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['currency']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} {self.amount} {self.get_currency_display()}"


class GoldMassConversionRate(models.Model):
    """Exchange rates for Gold and Mass"""
    # EGP to Gold rate: 1 EGP = ? Gold
    egp_to_gold = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal('10.00'))
    # EGP to Mass rate: 1 EGP = ? Mass
    egp_to_mass = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal('5.00'))
    
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rate_updates'
    )
    
    class Meta:
        verbose_name_plural = 'Gold/Mass Conversion Rates'
    
    @classmethod
    def get_current_rates(cls):
        """Get latest conversion rates"""
        return cls.objects.first() or cls.objects.create()
    
    def __str__(self):
        return f"1 EGP = {self.egp_to_gold} Gold = {self.egp_to_mass} Mass"


class SubscriptionTransaction(models.Model):
    """Track subscription purchases separately"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscription_transactions')
    plan = models.ForeignKey('accounts.SubscriptionPlan', on_delete=models.CASCADE)
    amount_egp = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed')],
        default='pending'
    )
    transaction = models.ForeignKey(Transaction, on_delete=models.SET_NULL, null=True, blank=True)
    
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.plan.name} ({self.status})"


class FinancialReport(models.Model):
    """Daily/monthly financial reports for platform"""
    PERIOD_CHOICES = (
        ('daily', 'Daily'),
        ('monthly', 'Monthly'),
    )
    
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES)
    date = models.DateField()  # Date or first day of month
    
    # Revenue by currency
    total_egp_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_gold_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_mass_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Transactions
    transaction_count = models.PositiveIntegerField(default=0)
    order_count = models.PositiveIntegerField(default=0)
    subscription_count = models.PositiveIntegerField(default=0)
    
    # Users
    new_users = models.PositiveIntegerField(default=0)
    new_dealers = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    
    class Meta:
        ordering = ['-date']
        unique_together = ('period', 'date')
    
    def __str__(self):
        return f"{self.get_period_display()} Report - {self.date}"
