"""
Admin panel APIs for managing users, dealers, plans, and financial reports
"""
from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta, datetime
from config.permissions import IsAdmin
from django_filters.rest_framework import DjangoFilterBackend
from config.accounts.models import User, DealerProfile, SubscriptionPlan
from config.accounts.serializers import UserDetailSerializer, DealerProfileSerializer, SubscriptionPlanSerializer
from config.payments.models import Transaction, FinancialReport, GoldMassConversionRate
from config.payments.serializers import GoldMassConversionRateSerializer
from config.products.models import Product
from config.orders.models import Order


class AdminUserManagementViewSet(viewsets.ModelViewSet):
    """Admin user management"""
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [IsAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['role', 'is_approved']
    ordering = ['-created_at']
    
    @action(detail=True, methods=['post'])
    def approve_dealer(self, request, pk=None):
        """Approve a dealer account"""
        user = self.get_object()
        if user.role != 'dealer':
            return Response(
                {'detail': 'User is not a dealer'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.is_approved = True
        user.save()
        
        return Response({
            'detail': 'Dealer approved',
            'user': UserDetailSerializer(user).data
        })
    
    @action(detail=True, methods=['post'])
    def suspend_user(self, request, pk=None):
        """Suspend user account"""
        user = self.get_object()
        reason = request.data.get('reason', 'Not specified')
        
        user.is_active = False
        user.save()
        
        return Response({
            'detail': f'User suspended: {reason}',
            'user': UserDetailSerializer(user).data
        })
    
    @action(detail=True, methods=['post'])
    def activate_user(self, request, pk=None):
        """Activate user account"""
        user = self.get_object()
        user.is_active = True
        user.save()
        
        return Response({
            'detail': 'User activated',
            'user': UserDetailSerializer(user).data
        })


class AdminDealerManagementViewSet(viewsets.ModelViewSet):
    """Admin dealer management"""
    queryset = DealerProfile.objects.all()
    serializer_class = DealerProfileSerializer
    permission_classes = [IsAdmin]
    ordering = ['-created_at']
    
    @action(detail=True, methods=['post'])
    def change_subscription(self, request, pk=None):
        """Change dealer subscription plan"""
        dealer_profile = self.get_object()
        plan_id = request.data.get('plan_id')
        
        plan = get_object_or_404(SubscriptionPlan, id=plan_id)
        
        dealer_profile.subscription_plan = plan
        dealer_profile.subscription_start_date = timezone.now()
        dealer_profile.subscription_end_date = timezone.now() + timedelta(days=plan.duration_days)
        dealer_profile.save()
        
        return Response({
            'detail': f'Subscription changed to {plan.get_name_display()}',
            'dealer': DealerProfileSerializer(dealer_profile).data
        })


class AdminProductModerationViewSet(viewsets.ReadOnlyModelViewSet):
    """Admin product moderation"""
    queryset = Product.objects.all()
    permission_classes = [IsAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'category']
    ordering = ['created_at']
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve product"""
        product = self.get_object()
        product.status = 'approved'
        product.reviewed_by = request.user
        product.reviewed_at = timezone.now()
        product.publish_date = timezone.now()
        
        if product.listing_duration_days:
            product.expires_at = timezone.now() + timedelta(days=product.listing_duration_days)
        
        product.save()
        
        return Response({'detail': 'Product approved'})
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject product"""
        product = self.get_object()
        reason = request.data.get('reason', 'Not specified')
        
        product.status = 'rejected'
        product.rejection_reason = reason
        product.reviewed_by = request.user
        product.reviewed_at = timezone.now()
        product.save()
        
        return Response({'detail': f'Product rejected: {reason}'})


class AdminFinancialReportView(generics.GenericAPIView):
    """Admin financial reports"""
    permission_classes = [IsAdmin]
    
    def get(self, request):
        """Get financial report for date range"""
        from_date = request.query_params.get('from_date')
        to_date = request.query_params.get('to_date')
        
        # Parse dates
        if not from_date or not to_date:
            from_date = (timezone.now() - timedelta(days=30)).date()
            to_date = timezone.now().date()
        else:
            from_date = datetime.fromisoformat(from_date).date()
            to_date = datetime.fromisoformat(to_date).date()
        
        # Get transactions
        transactions = Transaction.objects.filter(
            created_at__date__gte=from_date,
            created_at__date__lte=to_date,
            status='completed'
        )
        
        # Calculate totals
        egp_revenue = sum(t.amount for t in transactions if t.currency == 'egp')
        gold_revenue = sum(t.amount for t in transactions if t.currency == 'gold')
        mass_revenue = sum(t.amount for t in transactions if t.currency == 'mass')
        
        # Get order stats
        orders = Order.objects.filter(
            created_at__date__gte=from_date,
            created_at__date__lte=to_date,
            status='paid'
        )
        
        # Get user stats
        new_users = User.objects.filter(
            created_at__date__gte=from_date,
            created_at__date__lte=to_date
        ).count()
        
        new_dealers = User.objects.filter(
            created_at__date__gte=from_date,
            created_at__date__lte=to_date,
            role='dealer'
        ).count()
        
        return Response({
            'period': {
                'from': from_date,
                'to': to_date
            },
            'revenue': {
                'egp': float(egp_revenue),
                'gold': float(gold_revenue),
                'mass': float(mass_revenue)
            },
            'transactions': {
                'count': transactions.count(),
                'by_type': {
                    'purchases': transactions.filter(transaction_type='purchase').count(),
                    'refunds': transactions.filter(transaction_type='refund').count(),
                    'conversions': transactions.filter(transaction_type='conversion').count(),
                    'subscriptions': transactions.filter(transaction_type='subscription').count(),
                }
            },
            'orders': {
                'count': orders.count(),
                'total_value': float(sum(o.total_amount for o in orders))
            },
            'users': {
                'new_total': new_users,
                'new_dealers': new_dealers
            }
        })


class AdminConversionRateView(generics.RetrieveUpdateAPIView):
    """Admin conversion rate management"""
    serializer_class = GoldMassConversionRateSerializer
    permission_classes = [IsAdmin]
    
    def get_object(self):
        return GoldMassConversionRate.get_current_rates()
