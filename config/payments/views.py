from decimal import Decimal
from django.db import transaction
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.utils import timezone

from config.payments.models import Transaction, GoldMassConversionRate, SubscriptionTransaction
from config.payments.serializers import (
    GoldMassConversionRateSerializer, BuyGoldSerializer, BuyMassSerializer,
    TransactionSerializer, TransactionListSerializer, SubscriptionTransactionSerializer
)
from config.wallet_utils import WalletManager, CurrencyConverter
from config.permissions import IsAdmin
from django_filters.rest_framework import DjangoFilterBackend


class ConversionRateView(generics.RetrieveUpdateAPIView):
    """Get/update Gold and Mass conversion rates"""
    serializer_class = GoldMassConversionRateSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_object(self):
        return GoldMassConversionRate.get_current_rates()
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH']:
            return [IsAdmin()]
        return [permissions.AllowAny()]


class BuyGoldView(APIView):
    """Buy Gold using EGP"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = BuyGoldSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        amount_egp = serializer.validated_data['amount_egp']
        user = request.user
        
        # Perform conversion
        success, gold_amount, error = CurrencyConverter.buy_gold(user, amount_egp)
        
        if not success:
            return Response(
                {'detail': error},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({
            'detail': 'Gold purchased successfully',
            'amount_egp': float(amount_egp),
            'gold_received': float(gold_amount),
            'new_balances': {
                'egp': float(WalletManager.get_balance(user, 'egp')),
                'gold': float(WalletManager.get_balance(user, 'gold')),
                'mass': float(WalletManager.get_balance(user, 'mass')),
            }
        }, status=status.HTTP_200_OK)


class BuyMassView(APIView):
    """Buy Mass using EGP"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = BuyMassSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        amount_egp = serializer.validated_data['amount_egp']
        user = request.user
        
        # Perform conversion
        success, mass_amount, error = CurrencyConverter.buy_mass(user, amount_egp)
        
        if not success:
            return Response(
                {'detail': error},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({
            'detail': 'Mass purchased successfully',
            'amount_egp': float(amount_egp),
            'mass_received': float(mass_amount),
            'new_balances': {
                'egp': float(WalletManager.get_balance(user, 'egp')),
                'gold': float(WalletManager.get_balance(user, 'gold')),
                'mass': float(WalletManager.get_balance(user, 'mass')),
            }
        }, status=status.HTTP_200_OK)


class TransactionHistoryView(generics.ListAPIView):
    """List user transactions"""
    serializer_class = TransactionListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['currency', 'transaction_type', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)


class TransactionDetailView(generics.RetrieveAPIView):
    """Get transaction details"""
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)


class SubscriptionTransactionHistoryView(generics.ListAPIView):
    """List subscription transaction history"""
    serializer_class = SubscriptionTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering = ['-created_at']
    
    def get_queryset(self):
        return SubscriptionTransaction.objects.filter(user=self.request.user)
    

