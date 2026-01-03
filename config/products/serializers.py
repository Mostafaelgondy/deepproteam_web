from rest_framework import serializers
from config.products.models import Product, Category, ProductImage, ProductReview
from config.permissions import is_admin_user
from django.contrib.auth import get_user_model

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'description', 'is_active')


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('id', 'image', 'alt_text')


class ProductReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = ProductReview
        fields = ('id', 'user', 'rating', 'title', 'comment', 'is_verified_purchase', 'created_at')
        read_only_fields = ('id', 'user', 'is_verified_purchase', 'created_at')


class ProductListSerializer(serializers.ModelSerializer):
    """Simplified product serializer for listing"""
    dealer = serializers.StringRelatedField(read_only=True)
    category = CategorySerializer(read_only=True)
    avg_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ('id', 'name', 'slug', 'description', 'price_egp', 'price_gold', 'price_mass',
                  'image', 'stock', 'category', 'dealer', 'is_featured', 'created_at',
                  'avg_rating', 'review_count')
    
    def get_avg_rating(self, obj):
        reviews = obj.reviews.all()
        if not reviews:
            return None
        return sum(r.rating for r in reviews) / len(reviews)
    
    def get_review_count(self, obj):
        return obj.reviews.count()


class ProductDetailSerializer(serializers.ModelSerializer):
    """Full product details serializer"""
    dealer = serializers.StringRelatedField(read_only=True)
    dealer_id = serializers.IntegerField(source='dealer.id', read_only=True)
    category = CategorySerializer(read_only=True)
    additional_images = ProductImageSerializer(many=True, read_only=True)
    reviews = ProductReviewSerializer(many=True, read_only=True)
    avg_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ('id', 'name', 'slug', 'description', 'price_egp', 'price_gold', 'price_mass',
                  'primary_payment_type', 'image', 'video', 'stock', 'status', 'rejection_reason',
                  'category', 'dealer', 'dealer_id', 'is_featured', 'is_active', 'expires_at',
                  'created_at', 'updated_at', 'publish_date', 'additional_images', 'reviews',
                  'avg_rating', 'review_count', 'can_edit')
        read_only_fields = ('id', 'status', 'rejection_reason', 'reviewed_by', 'reviewed_at',
                           'created_at', 'updated_at', 'publish_date')
    
    def get_avg_rating(self, obj):
        reviews = obj.reviews.all()
        if not reviews:
            return None
        return sum(r.rating for r in reviews) / len(reviews)
    
    def get_review_count(self, obj):
        return obj.reviews.count()
    
    def get_can_edit(self, obj):
        request = self.context.get('request')
        if not request or not request.user:
            return False
        return obj.dealer == request.user or is_admin_user(request.user)


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """Create/Update product serializer - for dealers"""
    category_id = serializers.IntegerField(write_only=True)
    additional_images = serializers.ListField(
        child=serializers.ImageField(),
        required=False,
        write_only=True
    )
    
    class Meta:
        model = Product
        fields = ('name', 'description', 'price_egp', 'price_gold', 'price_mass',
                  'primary_payment_type', 'image', 'video', 'stock', 'is_featured',
                  'category_id', 'listing_duration_days', 'additional_images')
    
    def validate(self, data):
        """Ensure at least one price is set"""
        if not any([data.get('price_egp'), data.get('price_gold'), data.get('price_mass')]):
            raise serializers.ValidationError("At least one price must be set")
        return data
    
    def create(self, validated_data):
        """Create product with moderation"""
        from config.wallet_utils import WalletManager
        from config.accounts.models import DealerProfile
        
        additional_images = validated_data.pop('additional_images', [])
        category_id = validated_data.pop('category_id')
        category = Category.objects.get(id=category_id)
        
        user = self.context['request'].user
        dealer_profile = DealerProfile.objects.get(user=user)
        
        # Check subscription and free product rule
        can_publish, message = dealer_profile.can_publish_product()
        if not can_publish:
            raise serializers.ValidationError({"subscription": message})
        
        # Create product
        product = Product.objects.create(
            dealer=user,
            category=category,
            status='pending',  # Start as pending review
            **validated_data
        )
        
        # Mark free product as used if this is the first
        if not dealer_profile.has_used_free_product:
            dealer_profile.has_used_free_product = True
            dealer_profile.products_published += 1
            dealer_profile.save()
        else:
            # Charge subscription if exists
            if dealer_profile.subscription_plan:
                # Subscription allows publishing, just update count
                dealer_profile.products_published += 1
                dealer_profile.save()
        
        # Add images
        for image in additional_images:
            ProductImage.objects.create(product=product, image=image)
        
        return product
    
    def update(self, instance, validated_data):
        """Update product"""
        additional_images = validated_data.pop('additional_images', None)
        category_id = validated_data.pop('category_id', None)
        
        # Update basic fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if category_id:
            instance.category_id = category_id
        
        instance.save()
        
        # Update images if provided
        if additional_images is not None:
            instance.additional_images.all().delete()
            for image in additional_images:
                ProductImage.objects.create(product=instance, image=image)
        
        return instance
    dealer_name = serializers.CharField(source='dealer.username', read_only=True)

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ('dealer',)
