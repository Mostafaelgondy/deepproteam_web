from rest_framework import serializers
from django.contrib.auth import get_user_model
from config.accounts.models import (
    User, DealerProfile, SubscriptionPlan, 
    EGPWallet, GoldWallet, MassWallet
)
from config.wallet_utils import WalletManager

User = get_user_model()


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = ('id', 'name', 'price_egp', 'max_products', 'allows_videos', 
                  'ads_enabled', 'duration_days', 'description', 'is_active')


class WalletSerializer(serializers.Serializer):
    """Combined wallet balance serializer"""
    egp = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    gold = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    mass = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    
    def to_representation(self, instance):
        """Instance is the user object"""
        return {
            'egp': WalletManager.get_balance(instance, 'egp'),
            'gold': WalletManager.get_balance(instance, 'gold'),
            'mass': WalletManager.get_balance(instance, 'mass'),
        }


class DealerProfileSerializer(serializers.ModelSerializer):
    subscription_plan = SubscriptionPlanSerializer(read_only=True)
    can_publish = serializers.SerializerMethodField()
    is_subscription_active = serializers.SerializerMethodField()
    
    class Meta:
        model = DealerProfile
        fields = ('business_name', 'business_description', 'subscription_plan',
                  'subscription_start_date', 'subscription_end_date', 'products_published',
                  'has_used_free_product', 'rating', 'total_sales', 'can_publish',
                  'is_subscription_active')
        read_only_fields = ('products_published', 'has_used_free_product', 
                           'rating', 'total_sales', 'subscription_start_date',
                           'subscription_end_date')
    
    def get_can_publish(self, obj):
        can_publish, msg = obj.can_publish_product()
        return can_publish
    
    def get_is_subscription_active(self, obj):
        return obj.is_subscription_active()


class UserSerializer(serializers.ModelSerializer):
    """Comprehensive user serializer"""
    dealer_profile = DealerProfileSerializer(read_only=True)
    wallet = WalletSerializer(source='*', read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'role',
                  'phone_number', 'address', 'email_verified', 'is_approved',
                  'created_at', 'dealer_profile', 'wallet')
        read_only_fields = ('id', 'created_at', 'is_approved', 'email_verified', 'role')


class UserDetailSerializer(serializers.ModelSerializer):
    """User details with wallet info"""
    wallet = WalletSerializer(source='*', read_only=True)
    dealer_profile = DealerProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'role',
                  'phone_number', 'address', 'email_verified', 'created_at',
                  'dealer_profile', 'wallet')
        read_only_fields = ('id', 'username', 'created_at', 'role')


class RegisterSerializer(serializers.ModelSerializer):
    """User registration serializer"""
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        min_length=8
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    role = serializers.ChoiceField(
        choices=['client', 'dealer'],
        default='client'
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'first_name',
                  'last_name', 'phone_number', 'address', 'role')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True},
        }

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered")
        return value

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match"})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone_number=validated_data.get('phone_number', ''),
            address=validated_data.get('address', ''),
            role=validated_data.get('role', 'client'),
            is_approved=True if validated_data.get('role') == 'client' else False
        )
        
        # Create wallets for user
        WalletManager.get_or_create_wallets(user)
        
        # Create dealer profile if user is dealer
        if validated_data.get('role') == 'dealer':
            DealerProfile.objects.create(user=user)
        
        return user


class LoginSerializer(serializers.Serializer):
    """User login serializer"""
    username = serializers.CharField(required=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class PasswordResetConfirmSerializer(serializers.Serializer):
    uidb64 = serializers.CharField(required=True)
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        min_length=8
    )
    new_password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, data):
        if data['new_password'] != data['new_password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match"})
        return data


class UserUpdateSerializer(serializers.ModelSerializer):
    """Update user profile information"""
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone_number', 'address', 'email')
        extra_kwargs = {
            'email': {'required': False},
        }

class PasswordResetConfirmSerializer(serializers.Serializer):
    uidb64 = serializers.CharField(required=True)
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    new_password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    def validate(self, data):
        if data['new_password'] != data['new_password2']:
            raise serializers.ValidationError({"new_password": "Password fields didn't match."})
        return data
