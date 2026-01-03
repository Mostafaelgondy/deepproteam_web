from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta

from config.products.models import Product, Category, ProductImage, ProductReview
from config.products.serializers import (
    CategorySerializer, ProductListSerializer, ProductDetailSerializer,
    ProductCreateUpdateSerializer, ProductReviewSerializer
)
from config.permissions import IsDealer, IsDealerOwner, IsAdmin, IsOwnerOrAdmin
from config.accounts.models import DealerProfile
from config.wallet_utils import WalletManager


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """List and retrieve product categories"""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'


class ProductViewSet(viewsets.ModelViewSet):
    """Product CRUD with moderation and subscription enforcement"""
    queryset = Product.objects.all()
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'dealer', 'status', 'is_featured']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'price_egp', 'rating']
    ordering = ['-created_at']
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update' or self.action == 'partial_update':
            return ProductCreateUpdateSerializer
        elif self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductListSerializer
    
    def get_queryset(self):
        """Filter products based on user role"""
        if self.action == 'retrieve' or self.action == 'list':
            # Public users see only approved products
            if not self.request.user.is_authenticated:
                return Product.objects.filter(status='approved', is_active=True)
            
            # Admin sees all
            user = self.request.user
            if bool(getattr(user, 'is_staff', False) or getattr(user, 'is_superuser', False) or getattr(user, 'role', None) == 'admin'):
                return Product.objects.all()
            
            # Dealers see their own products + approved others
            if getattr(user, 'role', None) == 'dealer':
                return Product.objects.filter(
                    status__in=['approved', 'rejected', 'suspended']
                ) | Product.objects.filter(dealer=self.request.user)
            
            # Clients see approved products
            return Product.objects.filter(status='approved', is_active=True)
        
        # For edit actions, return all
        return Product.objects.all()
    
    def get_permissions(self):
        """Set permissions per action"""
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        elif self.action in ['create']:
            return [permissions.IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            # Owner or admin allowed
            return [IsOwnerOrAdmin()]
        return [permissions.IsAuthenticated()]
    
    def perform_create(self, serializer):
        """Create product - enforces subscription rules"""
        user = self.request.user
        
        # Only dealers and admins can create products
        if user.role not in ['dealer', 'admin']:
            raise PermissionDenied('Only dealers can create products')
        
        # Ensure dealer profile exists
        try:
            dealer_profile = DealerProfile.objects.get(user=user)
        except DealerProfile.DoesNotExist:
            raise PermissionDenied('Dealer profile not found')
        
        # Check subscription rules
        can_publish, message = dealer_profile.can_publish_product()
        if not can_publish:
            raise PermissionDenied(message)
        
        # Check if user can upload videos
        if serializer.validated_data.get('video'):
            if not dealer_profile.subscription_plan or not dealer_profile.subscription_plan.allows_videos:
                raise PermissionDenied('Video uploads only available for Pro and Enterprise plans')
        
        # Save product
        product = serializer.save(dealer=user)
        
        # Mark as free product used if first
        if not dealer_profile.has_used_free_product:
            dealer_profile.has_used_free_product = True
            dealer_profile.save()
    
    def perform_update(self, serializer):
        """Update product"""
        product = self.get_object()
        
        # Only dealer owner and admin can update
        if product.dealer != self.request.user and self.request.user.role != 'admin':
            raise PermissionDenied('You can only edit your own products')
        
        serializer.save()
    
    def perform_destroy(self, instance):
        """Delete product"""
        if instance.dealer != self.request.user and self.request.user.role != 'admin':
            raise PermissionDenied('You can only delete your own products')
        
        instance.delete()
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_products(self, request):
        """Get current dealer's products"""
        if request.user.role != 'dealer':
            return Response(
                {'detail': 'Only dealers can view their products'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        products = Product.objects.filter(dealer=request.user).order_by('-created_at')
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def approve(self, request, slug=None):
        """Admin approves a product"""
        product = self.get_object()
        product.status = 'approved'
        product.reviewed_by = request.user
        product.reviewed_at = timezone.now()
        product.publish_date = timezone.now()
        
        # Set expiry date
        if product.listing_duration_days:
            product.expires_at = timezone.now() + timedelta(days=product.listing_duration_days)
        
        product.save()
        
        return Response({
            'detail': 'Product approved',
            'product': ProductDetailSerializer(product, context={'request': request}).data
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def reject(self, request, slug=None):
        """Admin rejects a product"""
        product = self.get_object()
        reason = request.data.get('reason', 'Not specified')
        
        product.status = 'rejected'
        product.rejection_reason = reason
        product.reviewed_by = request.user
        product.reviewed_at = timezone.now()
        product.save()
        
        return Response({
            'detail': 'Product rejected',
            'reason': reason
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def suspend(self, request, slug=None):
        """Admin suspends a product"""
        product = self.get_object()
        reason = request.data.get('reason', 'Not specified')
        
        product.status = 'suspended'
        product.save()
        
        return Response({'detail': f'Product suspended: {reason}'})
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def add_review(self, request, slug=None):
        """Add a review to product"""
        product = self.get_object()
        
        # Check if user purchased this product
        from config.orders.models import OrderItem
        purchased = OrderItem.objects.filter(
            product=product,
            order__user=request.user,
            order__status='delivered'
        ).exists()
        
        rating = request.data.get('rating')
        title = request.data.get('title')
        comment = request.data.get('comment')
        
        if not all([rating, title, comment]):
            return Response(
                {'detail': 'rating, title, and comment required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        review, created = ProductReview.objects.update_or_create(
            product=product,
            user=request.user,
            defaults={
                'rating': rating,
                'title': title,
                'comment': comment,
                'is_verified_purchase': purchased
            }
        )
        
        serializer = ProductReviewSerializer(review)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

