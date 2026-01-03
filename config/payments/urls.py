from django.urls import path
from config.payments.views import (
    ConversionRateView, BuyGoldView, BuyMassView,
    TransactionHistoryView, TransactionDetailView,
    SubscriptionTransactionHistoryView
)

urlpatterns = [
    # Shop - Buy Gold/Mass
    path('shop/rates/', ConversionRateView.as_view(), name='conversion_rates'),
    path('shop/buy-gold/', BuyGoldView.as_view(), name='buy_gold'),
    path('shop/buy-mass/', BuyMassView.as_view(), name='buy_mass'),
    
    # Transaction History
    path('transactions/', TransactionHistoryView.as_view(), name='transaction_history'),
    path('transactions/<int:pk>/', TransactionDetailView.as_view(), name='transaction_detail'),
    path('subscriptions/', SubscriptionTransactionHistoryView.as_view(), name='subscription_history'),
]

