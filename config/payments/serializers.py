from rest_framework import serializers
from config.payments.models import Transaction, GoldMassConversionRate, SubscriptionTransaction


class GoldMassConversionRateSerializer(serializers.ModelSerializer):
    """Serializer for conversion rates"""
    class Meta:
        model = GoldMassConversionRate
        fields = ('egp_to_gold', 'egp_to_mass', 'updated_at')


class BuyGoldSerializer(serializers.Serializer):
    """Buy Gold using EGP"""
    amount_egp = serializers.DecimalField(max_digits=15, decimal_places=2, min_value=0.01)


class BuyMassSerializer(serializers.Serializer):
    """Buy Mass using EGP"""
    amount_egp = serializers.DecimalField(max_digits=15, decimal_places=2, min_value=0.01)


class TransactionSerializer(serializers.ModelSerializer):
    """Serialize transaction records"""
    user = serializers.StringRelatedField(read_only=True)
    order_id = serializers.IntegerField(source='order.id', read_only=True, allow_null=True)
    product_id = serializers.IntegerField(source='product.id', read_only=True, allow_null=True)

    class Meta:
        model = Transaction
        fields = ('id', 'user', 'transaction_type', 'currency', 'amount', 'status',
                  'description', 'order_id', 'product_id', 'created_at', 'completed_at')
        read_only_fields = ('id', 'user', 'status', 'created_at', 'completed_at')


class TransactionListSerializer(serializers.ModelSerializer):
    """Simplified transaction serializer for lists"""
    class Meta:
        model = Transaction
        fields = ('id', 'transaction_type', 'currency', 'amount', 'status', 'description', 'created_at')


class SubscriptionTransactionSerializer(serializers.ModelSerializer):
    """Subscription transaction serializer"""
    plan_name = serializers.CharField(source='plan.name', read_only=True)
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = SubscriptionTransaction
        fields = ('id', 'user', 'plan', 'plan_name', 'amount_egp', 'status',
                  'start_date', 'end_date', 'created_at', 'completed_at')
        read_only_fields = ('id', 'user', 'status', 'created_at', 'completed_at')


