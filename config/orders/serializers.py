from rest_framework import serializers
from config.orders.models import Order, OrderItem, Cart, CartItem
from config.products.serializers import ProductListSerializer
from decimal import Decimal


class OrderItemSerializer(serializers.ModelSerializer):
    """Order item serializer"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    product = ProductListSerializer(read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_name', 'quantity', 'price_egp', 
                  'price_gold', 'price_mass', 'total_price')


class OrderListSerializer(serializers.ModelSerializer):
    """Order list serializer"""
    items_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = ('id', 'status', 'total_amount', 'payment_method', 'created_at', 
                  'paid_at', 'delivered_at', 'items_count')
    
    def get_items_count(self, obj):
        return obj.items.count()


class OrderDetailSerializer(serializers.ModelSerializer):
    """Detailed order serializer"""
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = ('id', 'status', 'total_amount', 'egp_amount', 'gold_amount', 'mass_amount',
                  'payment_method', 'shipping_address', 'shipping_phone', 'shipping_status',
                  'created_at', 'updated_at', 'paid_at', 'delivered_at', 'items', 'notes')
        read_only_fields = ('id', 'total_amount', 'egp_amount', 'gold_amount', 'mass_amount', 
                           'status', 'paid_at', 'delivered_at', 'created_at', 'updated_at')


class CreateOrderSerializer(serializers.ModelSerializer):
    """Create order from cart"""
    payment_method = serializers.ChoiceField(choices=['egp', 'gold', 'mass'])
    
    class Meta:
        model = Order
        fields = ('payment_method', 'shipping_address', 'shipping_phone', 'notes')


class CartItemSerializer(serializers.ModelSerializer):
    """Shopping cart item"""
    product = ProductListSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    total_price = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = ('id', 'product', 'product_id', 'quantity', 'total_price')
    
    def get_total_price(self, obj):
        return float(obj.get_total())


class CartSerializer(serializers.ModelSerializer):
    """Shopping cart serializer"""
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = ('id', 'items', 'total', 'updated_at')
    
    def get_total(self, obj):
        return float(obj.get_total())

