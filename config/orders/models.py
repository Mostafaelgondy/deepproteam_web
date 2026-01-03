from django.db import models
from django.conf import settings
from config.products.models import Product
from decimal import Decimal

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Payment'),
        ('paid', 'Paid'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    )
    
    PAYMENT_METHOD_CHOICES = (
        ('egp', 'Egyptian Pound'),
        ('gold', 'Gold'),
        ('mass', 'Mass'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='orders', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Payment info
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='egp')
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    egp_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    gold_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    mass_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Shipping info
    shipping_address = models.TextField(blank=True, null=True)
    shipping_phone = models.CharField(max_length=15, blank=True, null=True)
    shipping_status = models.CharField(max_length=100, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    # Notes
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Order #{self.id} - {self.user.username} ({self.get_status_display()})"
    
    def get_total_price(self):
        """Calculate total from items"""
        return sum(item.total_price for item in self.items.all())
    
    def calculate_totals(self):
        """Recalculate totals from items"""
        self.total_amount = self.get_total_price()
        self.save()


class OrderItem(models.Model):
    """Individual items in an order"""
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    # Price snapshot at time of purchase
    price_egp = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    price_gold = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    price_mass = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Total for this item
    total_price = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"


class Cart(models.Model):
    """Shopping cart for users"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def get_total(self):
        """Get cart total in EGP"""
        return sum(item.get_total() for item in self.items.all())
    
    def clear(self):
        """Clear all items from cart"""
        self.items.all().delete()
    
    def __str__(self):
        return f"Cart for {self.user.username}"


class CartItem(models.Model):
    """Items in shopping cart"""
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    
    class Meta:
        unique_together = ('cart', 'product')
    
    def get_total(self):
        """Get total price for this item in EGP"""
        price = self.product.price_egp or Decimal('0.00')
        return price * self.quantity
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
