from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model, authenticate
from django.urls import reverse
from django.core import signing
from django.db import transaction

from config.permissions import IsAdmin, IsDealer, IsClient, is_admin_user
from config.wallet_utils import WalletManager
from .serializers import (
    RegisterSerializer, UserSerializer, UserDetailSerializer,
    PasswordResetSerializer, PasswordResetConfirmSerializer,
    LoginSerializer, UserUpdateSerializer, DealerProfileSerializer,
    SubscriptionPlanSerializer
)
from config.accounts.models import User, DealerProfile, SubscriptionPlan

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """User registration endpoint"""
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    
    @transaction.atomic
    def perform_create(self, serializer):
        return serializer.save()


class LoginView(generics.GenericAPIView):
    """User login endpoint with JWT and role-based redirect"""
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        user = authenticate(username=username, password=password)
        
        if user is None:
            return Response(
                {'detail': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        refresh = RefreshToken.for_user(user)
        
        # Determine redirect URL based on user role
        redirect_url = '/'
        if is_admin_user(user):
            redirect_url = '/admin/dashboard/'
        elif getattr(user, 'role', None) == 'dealer':
            redirect_url = '/dealer/dashboard/'
        elif getattr(user, 'role', None) == 'client':
            redirect_url = '/shop/'
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserDetailSerializer(user).data,
            'redirect_url': redirect_url
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """User logout endpoint - blacklist token"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            if not refresh_token:
                return Response(
                    {'detail': 'Refresh token required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response(
                {'detail': 'Successfully logged out'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class UserDetailView(generics.RetrieveUpdateAPIView):
    """Get/update current user details"""
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
    
    def get_serializer_class(self):
        if self.request.method == 'PUT' or self.request.method == 'PATCH':
            return UserUpdateSerializer
        return UserDetailSerializer


class UserProfileView(generics.RetrieveUpdateAPIView):
    """User profile with wallet info"""
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class DealerProfileView(generics.RetrieveUpdateAPIView):
    """Get/update dealer profile"""
    serializer_class = DealerProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        dealer_profile = get_object_or_404(DealerProfile, user=self.request.user)
        return dealer_profile
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return DealerProfileSerializer
        return DealerProfileSerializer


class SubscriptionPlansView(generics.ListAPIView):
    """List all subscription plans"""
    queryset = SubscriptionPlan.objects.filter(is_active=True)
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [permissions.AllowAny]


class PurchaseSubscriptionView(generics.CreateAPIView):
    """Purchase a subscription plan"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        plan_id = request.data.get('plan_id')
        
        if not plan_id:
            return Response(
                {'detail': 'plan_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        plan = get_object_or_404(SubscriptionPlan, id=plan_id, is_active=True)
        user = request.user
        
        # Check if user is dealer
        if getattr(user, 'role', None) != 'dealer':
            return Response(
                {'detail': 'Only dealers can purchase subscription plans'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Deduct EGP from wallet
        success, txn, error = WalletManager.deduct_from_wallet(
            user,
            plan.price_egp,
            'egp',
            f"Subscription: {plan.get_name_display()}",
            transaction_type='subscription'
        )
        
        if not success:
            return Response(
                {'detail': error},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update dealer profile with subscription
        from django.utils import timezone
        from datetime import timedelta
        
        dealer_profile = DealerProfile.objects.get(user=user)
        dealer_profile.subscription_plan = plan
        dealer_profile.subscription_start_date = timezone.now()
        dealer_profile.subscription_end_date = timezone.now() + timedelta(days=plan.duration_days)
        dealer_profile.save()
        
        return Response({
            'detail': f'Successfully subscribed to {plan.get_name_display()}',
            'plan': SubscriptionPlanSerializer(plan).data,
            'expires_at': dealer_profile.subscription_end_date
        }, status=status.HTTP_200_OK)


class PasswordResetRequestView(generics.GenericAPIView):
    """Request password reset - sends email"""
    serializer_class = PasswordResetSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        
        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Build reset URL
            reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"
            
            subject = "Password Reset Request"
            message = f"""
            Hello {user.first_name},
            
            Click the link below to reset your password:
            {reset_url}
            
            This link will expire in 24 hours.
            
            Best regards,
            {settings.PLATFORM_NAME}
            """
            
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
        
        except User.DoesNotExist:
            pass  # Don't reveal if email exists
        
        return Response({
            'detail': 'Password reset email sent if account exists'
        }, status=status.HTTP_200_OK)


class PasswordResetConfirmView(generics.GenericAPIView):
    """Confirm password reset with token"""
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uidb64 = serializer.validated_data['uidb64']
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']

        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {'detail': 'Invalid reset link'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if user is not None and default_token_generator.check_token(user, token):
            user.set_password(new_password)
            user.save()
            return Response({
                'detail': 'Password reset successful'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'detail': 'Invalid or expired reset link'
            }, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(generics.GenericAPIView):
    """Change password for authenticated user"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        new_password2 = request.data.get('new_password2')
        
        if not old_password or not new_password or not new_password2:
            return Response(
                {'detail': 'All fields required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not user.check_password(old_password):
            return Response(
                {'detail': 'Old password incorrect'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if new_password != new_password2:
            return Response(
                {'detail': 'New passwords do not match'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(new_password) < 8:
            return Response(
                {'detail': 'Password must be at least 8 characters'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(new_password)
        user.save()
        
        return Response({
            'detail': 'Password changed successfully'
        }, status=status.HTTP_200_OK)


class WalletBalanceView(APIView):
    """Get user wallet balances"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        return Response({
            'egp': float(WalletManager.get_balance(user, 'egp')),
            'gold': float(WalletManager.get_balance(user, 'gold')),
            'mass': float(WalletManager.get_balance(user, 'mass')),
        }, status=status.HTTP_200_OK)
        

class EmailVerificationConfirmView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, token):
        try:
            data = signing.loads(token, salt='email-verify', max_age=172800)
            User = get_user_model()
            user = User.objects.get(id=data['user_id'])
            user.email_verified = True
            user.save()
            return Response({'detail': 'Email verified successfully.'}, status=status.HTTP_200_OK)
        except Exception:
            return Response({'detail': 'Invalid or expired verification link.'}, status=status.HTTP_400_BAD_REQUEST)

from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

class AdminUserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = UserSerializer

    def get_queryset(self):
        User = get_user_model()
        return User.objects.all()
