from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from config.accounts.views import (
    RegisterView,
    LoginView,
    LogoutView,
    UserDetailView,
    UserProfileView,
    DealerProfileView,
    SubscriptionPlansView,
    PurchaseSubscriptionView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    ChangePasswordView,
    WalletBalanceView,
)

urlpatterns = [
    # Authentication
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User Profile
    path('me/', UserDetailView.as_view(), name='user_detail'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    
    # Wallet
    path('wallet/balance/', WalletBalanceView.as_view(), name='wallet_balance'),
    
    # Dealer Profile & Subscription
    path('dealer/profile/', DealerProfileView.as_view(), name='dealer_profile'),
    path('subscription/plans/', SubscriptionPlansView.as_view(), name='subscription_plans'),
    path('subscription/purchase/', PurchaseSubscriptionView.as_view(), name='purchase_subscription'),
    
    # Password Reset
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]
