from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend

from config.orders.models import Order, OrderItem, Cart, CartItem
from config.orders.serializers import (
    OrderDetailSerializer, OrderListSerializer, CreateOrderSerializer,
    CartSerializer, CartItemSerializer
)
from config.products.models import Product
from config.wallet_utils import WalletManager
from config.permissions import is_admin_user
from config.payments.payment_gateway import payment_gateway
from decimal import Decimal
from config.permissions import is_admin_user


class CartViewSet(viewsets.ViewSet):
    """Shopping cart management"""
    permission_classes = [permissions.IsAuthenticated]
    
    def list(self, request):
        """Get user's cart"""
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """Add item to cart"""
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)
        
        if not product_id:
            return Response(
                {'detail': 'product_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        product = get_object_or_404(Product, id=product_id, status='approved')
        cart, _ = Cart.objects.get_or_create(user=request.user)
        
        cart_item, created = CartItem.objects.update_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        """Remove item from cart"""
        product_id = request.data.get('product_id')
        
        if not product_id:
            return Response(
                {'detail': 'product_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cart = get_object_or_404(Cart, user=request.user)
        try:
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
            cart_item.delete()
            return Response({'detail': 'Item removed'}, status=status.HTTP_200_OK)
        except CartItem.DoesNotExist:
            return Response(
                {'detail': 'Item not in cart'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def clear(self, request):
        """Clear entire cart"""
        try:
            cart = Cart.objects.get(user=request.user)
            cart.clear()
            return Response({'detail': 'Cart cleared'}, status=status.HTTP_200_OK)
        except Cart.DoesNotExist:
            return Response(
                {'detail': 'Cart not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """Order management"""
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'payment_method']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return OrderDetailSerializer
        return OrderListSerializer
    
    @action(detail=False, methods=['post'])
    def create_from_cart(self, request):
        """Create order from shopping cart with comprehensive validation"""
        cart = get_object_or_404(Cart, user=request.user)
        
        if not cart.items.exists():
            return Response(
                {'detail': 'Cart is empty'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        payment_method = serializer.validated_data['payment_method']
        shipping_address = serializer.validated_data['shipping_address']
        shipping_phone = serializer.validated_data['shipping_phone']
        notes = serializer.validated_data.get('notes', '')
        
        with transaction.atomic():
            # Calculate totals with tax (5%)
            subtotal = cart.get_total()
            tax_rate = Decimal('0.05')  # 5% platform tax
            tax_amount = subtotal * tax_rate
            total_amount = subtotal + tax_amount
            
            # Validate sufficient funds in wallet
            user_balance = WalletManager.get_balance(request.user, payment_method)
            if user_balance < total_amount:
                return Response(
                    {'detail': f'Insufficient {payment_method.upper()} balance. Required: {total_amount}, Available: {user_balance}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create order
            order = Order.objects.create(
                user=request.user,
                payment_method=payment_method,
                total_amount=total_amount,
                shipping_address=shipping_address,
                shipping_phone=shipping_phone,
                notes=notes,
                status='pending'
            )
            
            # Add items to order
            for cart_item in cart.items.all():
                product = cart_item.product
                price_egp = product.price_egp or Decimal('0')
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=cart_item.quantity,
                    price_egp=product.price_egp,
                    price_gold=product.price_gold,
                    price_mass=product.price_mass,
                    total_price=price_egp * cart_item.quantity
                )
            
            # Clear cart
            cart.clear()
        
        return Response(
            {
                'detail': 'Order created. Proceed to payment.',
                'order': OrderDetailSerializer(order).data,
                'checkout': {
                    'subtotal': float(subtotal),
                    'tax_amount': float(tax_amount),
                    'total_amount': float(total_amount),
                    'payment_method': payment_method
                }
            },
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def process_payment(self, request, pk=None):
        """Process payment for order using payment gateway"""
        order = self.get_object()
        
        if order.user != request.user and not is_admin_user(request.user):
            return Response(
                {'detail': 'Not authorized'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if order.status != 'pending':
            return Response(
                {'detail': 'Order already processed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payment_method = order.payment_method
        total_amount = order.total_amount
        
        with transaction.atomic():
            # Process payment through gateway
            gateway_result = payment_gateway.process_payment(
                total_amount,
                payment_method,
                f"Order #{order.id}",
                metadata={'order_id': order.id, 'user_id': request.user.id}
            )
            
            if not gateway_result.success:
                return Response(
                    {'detail': f'Payment failed: {gateway_result.error}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Deduct from wallet after successful gateway processing
            success, txn, error = WalletManager.deduct_from_wallet(
                request.user,
                total_amount,
                payment_method,
                f"Order #{order.id} - Gateway: {gateway_result.transaction_id}",
                transaction_type='purchase',
                order=order
            )
            
            if not success:
                # Payment gateway succeeded but wallet deduction failed
                # In production, refund via gateway here
                return Response(
                    {'detail': f'Wallet deduction failed: {error}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update order status
            order.status = 'paid'
            order.paid_at = timezone.now()
            
            # Store payment amount by currency
            if payment_method == 'egp':
                order.egp_amount = total_amount
            elif payment_method == 'gold':
                order.gold_amount = total_amount
            elif payment_method == 'mass':
                order.mass_amount = total_amount
            
            order.save()
        
        return Response({
            'detail': 'Payment processed successfully',
            'order': OrderDetailSerializer(order).data,
            'payment': {
                'gateway_transaction': gateway_result.transaction_id,
                'status': 'completed',
                'amount': float(total_amount),
                'currency': payment_method
            }
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel order and refund"""
        order = self.get_object()
        
        if order.user != request.user and not is_admin_user(request.user):
            return Response(
                {'detail': 'Not authorized'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if order.status not in ['pending', 'paid']:
            return Response(
                {'detail': 'Cannot cancel this order'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            # Refund if paid
            if order.status == 'paid':
                amount = order.total_amount
                payment_method = order.payment_method
                
                success, txn, error = WalletManager.add_to_wallet(
                    order.user,
                    amount,
                    payment_method,
                    f"Refund for Order #{order.id}",
                    transaction_type='refund',
                    order=order
                )
                
                if not success:
                    return Response(
                        {'detail': error},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Update order status
            order.status = 'cancelled'
            order.save()
        
        return Response({
            'detail': 'Order cancelled',
            'order': OrderDetailSerializer(order).data
        }, status=status.HTTP_200_OK)

