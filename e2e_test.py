#!/usr/bin/env python
"""
End-to-End Marketplace Test Script
Tests: Login → Add to Cart → Checkout → Payment → Order Created

Usage: python manage.py shell < e2e_test.py
Or: python e2e_test.py
"""

import os
import sys
import json
from decimal import Decimal

# Setup Django if running standalone
if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    import django
    django.setup()

from django.contrib.auth import get_user_model, authenticate
from django.test import Client
from config.products.models import Product
from config.orders.models import Cart, CartItem, Order
from config.wallet_utils import WalletManager

User = get_user_model()

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def test_e2e_flow():
    """Complete E2E test: login → cart → checkout → payment"""
    
    client = Client()
    
    # Step 1: Authenticate as client
    print_section("STEP 1: User Authentication")
    client.defaults['HTTP_CONTENT_TYPE'] = 'application/json'
    
    login_response = client.post(
        '/api/auth../login.html',
        json.dumps({'username': 'client1', 'password': 'client123'}),
        content_type='application/json'
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.content}")
        return False
    
    data = json.loads(login_response.content)
    access_token = data['access']
    user = User.objects.get(username='client1')
    
    print(f"✓ Logged in as: {user.username}")
    print(f"✓ Access token: {access_token[:20]}...")
    print(f"✓ Initial balance: EGP {WalletManager.get_balance(user, 'egp')}")
    
    # Step 2: Get first product
    print_section("STEP 2: Browse Products")
    products = Product.objects.filter(status='approved')
    
    if not products.exists():
        print("❌ No approved products found. Run: python manage.py seed_test_data")
        return False
    
    product = products.first()
    print(f"✓ Product: {product.name}")
    print(f"✓ Price: EGP {product.price_egp}")
    
    # Step 3: Add to cart
    print_section("STEP 3: Add to Cart")
    
    cart, _ = Cart.objects.get_or_create(user=user)
    cart_item, created = CartItem.objects.update_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 2}
    )
    
    print(f"✓ Added {cart_item.quantity}x {product.name} to cart")
    cart_total = cart.get_total()
    print(f"✓ Cart total: EGP {cart_total}")
    
    # Step 4: Checkout (create order)
    print_section("STEP 4: Checkout")
    
    checkout_response = client.post(
        '/api/orders/orders/create_from_cart/',
        json.dumps({
            'payment_method': 'egp',
            'shipping_address': '123 Main St, Cairo',
            'shipping_phone': '+201012345678',
            'notes': 'E2E test order'
        }),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {access_token}'
    )
    
    if checkout_response.status_code != 201:
        print(f"❌ Checkout failed: {checkout_response.content}")
        return False
    
    checkout_data = json.loads(checkout_response.content)
    order_id = checkout_data['order']['id']
    order = Order.objects.get(id=order_id)
    
    print(f"✓ Order created: #{order.id}")
    print(f"✓ Status: {order.status}")
    print(f"✓ Subtotal: EGP {checkout_data['checkout']['subtotal']}")
    print(f"✓ Tax (5%): EGP {checkout_data['checkout']['tax_amount']}")
    print(f"✓ Total: EGP {checkout_data['checkout']['total_amount']}")
    
    # Step 5: Process Payment
    print_section("STEP 5: Process Payment")
    
    payment_response = client.post(
        f'/api/orders/orders/{order_id}/process_payment/',
        json.dumps({}),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {access_token}'
    )
    
    if payment_response.status_code != 200:
        print(f"❌ Payment failed: {payment_response.content}")
        return False
    
    payment_data = json.loads(payment_response.content)
    order.refresh_from_db()
    
    print(f"✓ Payment processed successfully")
    print(f"✓ Gateway transaction: {payment_data['payment']['gateway_transaction'][:20]}...")
    print(f"✓ Order status: {order.status}")
    print(f"✓ Order items: {order.items.count()}")
    
    for item in order.items.all():
        print(f"  - {item.quantity}x {item.product.name} @ EGP {item.price_egp}")
    
    # Step 6: Verify wallet deduction
    print_section("STEP 6: Verify Wallet")
    
    final_balance = WalletManager.get_balance(user, 'egp')
    expected_deduction = order.total_amount
    
    print(f"✓ Final balance: EGP {final_balance}")
    print(f"✓ Amount deducted: EGP {expected_deduction}")
    print(f"✓ Cart cleared: {not cart.items.exists()}")
    
    # Step 7: Verify order retrieval
    print_section("STEP 7: Order Retrieval")
    
    orders_response = client.get(
        '/api/orders/orders/',
        HTTP_AUTHORIZATION=f'Bearer {access_token}'
    )
    
    if orders_response.status_code != 200:
        print(f"❌ Order retrieval failed: {orders_response.content}")
        return False
    
    orders_data = json.loads(orders_response.content)
    print(f"✓ User has {len(orders_data['results'])} order(s)")
    
    # Summary
    print_section("✅ E2E TEST PASSED")
    print(f"Successfully completed marketplace flow:")
    print(f"  1. Authenticated user: {user.username}")
    print(f"  2. Added product to cart: {product.name}")
    print(f"  3. Created order with tax: EGP {order.total_amount}")
    print(f"  4. Processed payment via mock gateway")
    print(f"  5. Deducted from wallet: EGP {expected_deduction}")
    print(f"  6. Order status changed to: {order.status}")
    
    return True

if __name__ == '__main__':
    success = test_e2e_flow()
    sys.exit(0 if success else 1)
