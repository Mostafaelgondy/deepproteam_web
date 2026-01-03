# Production-Ready Marketplace Platform - Implementation Guide

## Project Overview

A scalable, production-ready marketplace built with **Django REST Framework** and **Vanilla JavaScript + Tailwind CSS**. Features include:

- **Multi-Currency Support**: EGP (real), Gold & Mass (virtual credits)
- **Subscription-Based Dealer System**: Starter, Pro, Enterprise plans
- **Atomic Wallet Operations**: Thread-safe, race-condition protected transactions
- **Product Moderation**: Admin approval workflow
- **Role-Based Access Control**: Admin, Dealer, Client roles
- **Comprehensive Admin Panel**: User management, financial reports, conversion rates

---

## Architecture Overview

### Database Models Structure

```
User (Custom User Model)
├── DealerProfile (For dealers only)
│   ├── SubscriptionPlan (Foreign Key)
│   ├── Wallets (EGP, Gold, Mass) - OneToOne per User
│   └── Products
└── Customer (Implicit via role='client')

Product
├── Category
├── Dealer (FK to User)
├── Images (ProductImage)
├── Reviews (ProductReview)
├── Status (pending/approved/rejected/suspended)
└── Prices (EGP, Gold, Mass)

Transaction (Audit Trail)
├── User
├── Type (purchase/refund/conversion/subscription)
├── Currency (egp/gold/mass)
├── Order (FK, nullable)
└── Product (FK, nullable)

Order
├── User
├── Items (OrderItem)
├── Cart (optional source)
└── Payments (via Transaction)
```

### API Structure

```
/api/
├── auth/                    # Authentication & User Management
│   ├── register/           # User registration
│   ├── login/              # JWT login
│   ├── logout/             # Token blacklist
│   ├── me/                 # Current user profile
│   ├── wallet/balance/     # Get wallet balances
│   ├── profile/            # Update user info
│   ├── dealer/profile/     # Dealer-specific profile
│   └── subscription/       # Plans & purchasing
├── shop/                   # Product Catalog
│   ├── products/           # List, create, update, delete
│   ├── products/{slug}/    # Product details
│   └── categories/         # Product categories
├── orders/                 # Cart & Orders
│   ├── cart/              # Shopping cart management
│   ├── orders/            # Order CRUD
│   └── orders/{id}/process_payment/
├── payments/              # Wallet & Transactions
│   ├── shop/buy-gold/    # Purchase Gold with EGP
│   ├── shop/buy-mass/    # Purchase Mass with EGP
│   ├── transactions/     # Transaction history
│   └── shop/rates/       # Conversion rates
└── admin/                # Admin APIs
    ├── users/           # User management
    ├── dealers/         # Dealer management
    ├── products/        # Product moderation
    └── reports/financial/
```

---

## Business Logic Implementation

### 1. Subscription & Product Publishing

**Rule**: First product free, subsequent products require active subscription

```python
# In DealerProfile.can_publish_product():

# First product is always free
if not self.has_used_free_product:
    return True, "Free first product available"

# After first product, need subscription
if not self.subscription_plan or not self.is_subscription_active():
    return False, "Subscription required"

# Check product limit
if self.subscription_plan.max_products > 0:
    active_count = self.get_active_product_count()
    if active_count >= self.subscription_plan.max_products:
        return False, f"Max products reached"

return True, "Can publish"
```

**Implementation**:
- Checked in `ProductCreateUpdateSerializer.create()`
- Uses `DealerProfile.can_publish_product()` method
- First product marks `has_used_free_product = True`
- Subsequent products require active subscription

### 2. Atomic Wallet Transactions

**Prevents Race Conditions**: Uses database-level locks via `select_for_update()`

```python
@transaction.atomic
def deduct_from_wallet(user, amount, currency, ...):
    if currency == 'egp':
        wallet = EGPWallet.objects.select_for_update().get(user=user)
        if wallet.balance < amount:
            return False, None, "Insufficient balance"
        wallet.balance = F('balance') - amount
        wallet.save()
    # ... similar for gold/mass
```

**Key Features**:
- Database-level locking prevents concurrent withdrawals
- `F()` expressions ensure atomic arithmetic
- Wrapped in `@transaction.atomic` for rollback capability
- Returns success/failure with error messages

### 3. Multi-Currency Payment Processing

**Supported Currencies**:
- **EGP**: Real currency (real money)
- **Gold**: Premium credit (1 EGP = 0.5 Gold)
- **Mass**: Regular credit (1 EGP = 0.05 Mass)

**Conversion**:
```python
# In CurrencyConverter class
egp_to_gold = amount_egp * rates.egp_to_gold
egp_to_mass = amount_egp * rates.egp_to_mass
```

**Order Payment**:
```python
# Customer selects payment method
POST /api/orders/orders/{id}/process_payment/

# Backend deducts from chosen currency wallet
success = WalletManager.deduct_from_wallet(
    user, total_amount, 'egp',  # or 'gold' or 'mass'
    f"Order #{order.id}"
)
```

### 4. Product Moderation

**Workflow**:
1. Dealer creates product → Status = `pending`
2. Admin reviews → `approved` or `rejected`
3. Only `approved` products visible to public
4. Admin can `suspend` active products

**Endpoints**:
```python
# Admin-only actions
POST /api/admin/products/{id}/approve/
POST /api/admin/products/{id}/reject/ {reason: "..."}
POST /api/admin/products/{id}/suspend/ {reason: "..."}
```

### 5. Role-Based Access Control

**Implemented via Permission Classes**:

```python
class IsAdmin(IsAuthenticated):
    def has_permission(self, request, view):
        return request.user.role == 'admin'

class IsDealer(IsAuthenticated):
    def has_permission(self, request, view):
        return request.user.role == 'dealer'
```

**Applied to Views**:
- `RegisterView`: AllowAny
- `ProductCreate`: Requires dealer role + subscription check
- `AdminUserManagement`: Requires admin role
- `BuyGoldView`: Requires authenticated user

---

## Security Implementation

### 1. Password Security

```python
# Automatic in Django User model
user.set_password(password)  # Hashes with PBKDF2

# Validation in serializer
'password': serializers.CharField(min_length=8)
```

### 2. CSRF Protection

```python
# Enabled in settings.py
MIDDLEWARE = [
    'django.middleware.csrf.CsrfViewMiddleware',
]

# For API, token required on state-changing requests
# Django automatically handles CSRF for forms
```

### 3. JWT Authentication

```python
# Token-based authentication
POST /api/auth../login.html
→ Returns access_token (60 min), refresh_token (1 day)

# Usage in requests
headers = {'Authorization': 'Bearer {access_token}'}

# Blacklist on logout
POST /api/auth/logout/
→ Blacklists token in DB
```

### 4. Backend-Enforced Rules

**Not Frontend-Only**:
- ✅ Subscription validation done in backend
- ✅ Product limits enforced in backend
- ✅ Permission checks on every API call
- ✅ Wallet balance verified before deduction

**Example - Product Publishing**:
```javascript
// Frontend shows button, but backend still validates
POST /api/shop/products/ {name: "...", ...}

// Backend checks:
dealer_profile = DealerProfile.objects.get(user=user)
can_publish, msg = dealer_profile.can_publish_product()
if not can_publish:
    raise PermissionDenied(msg)
```

### 5. SQL Injection Prevention

All queries use Django ORM with parameterized queries:
```python
# ✅ Safe
Product.objects.filter(name__icontains=search_term)

# ❌ Never do this
Product.objects.raw(f"SELECT * FROM products WHERE name LIKE '{term}'")
```

---

## Getting Started

### Prerequisites
- Python 3.9+
- PostgreSQL 12+ (production) or SQLite (dev)
- Virtual environment

### Step 1: Setup Environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### Step 2: Database Setup

```bash
# Create migrations (if not already created)
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create initial data
python manage.py init_platform
```

This creates:
- ✅ 3 Subscription Plans (Starter, Pro, Enterprise)
- ✅ 8 Product Categories
- ✅ Conversion Rates (1 EGP = 10 Gold, 5 Mass)
- ✅ Admin user (username: `admin`, password: `admin123`)

### Step 3: Run Development Server

```bash
python manage.py runserver

# Visit:
# - API: http://localhost:8000/api/
# - Admin: http://localhost:8000/admin/
# - Shop: http://localhost:8000/shop.html
```

---

## API Usage Examples

### Register User

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "email": "john@example.com",
    "password": "secure123",
    "password2": "secure123",
    "first_name": "John",
    "last_name": "Doe",
    "role": "client"
  }'
```

### Login

```bash
curl -X POST http://localhost:8000/api/auth../login.html \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "password": "secure123"}'

# Response:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {...}
}
```

### Buy Gold

```bash
curl -X POST http://localhost:8000/api/payments/shop/buy-gold/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {access_token}" \
  -d '{"amount_egp": 100}'

# Response:
{
  "detail": "Gold purchased successfully",
  "amount_egp": 100,
  "gold_received": 1000,
  "new_balances": {
    "egp": 900,
    "gold": 1000,
    "mass": 250
  }
}
```

### Create Product (Dealer)

```bash
curl -X POST http://localhost:8000/api/shop/products/ \
  -H "Authorization: Bearer {access_token}" \
  -F "name=Laptop Pro" \
  -F "description=High-end laptop" \
  -F "category_id=1" \
  -F "price_egp=5000" \
  -F "image=@laptop.jpg"

# Backend validates:
# ✅ User has dealer role
# ✅ Dealer profile exists
# ✅ Can publish (free product or has subscription)
# ✅ Can upload video (if Pro/Enterprise)
```

### Place Order

```bash
# 1. Add to cart
POST /api/orders/cart/add_item/
{"product_id": 1, "quantity": 2}

# 2. Create order from cart
POST /api/orders/orders/create_from_cart/
{
  "payment_method": "egp",
  "shipping_address": "123 Main St",
  "shipping_phone": "+201001234567"
}

# 3. Process payment
POST /api/orders/orders/1/process_payment/
# Deducts from wallet, creates Transaction record
```

---

## Deployment Checklist

### Before Going Live

- [ ] Set `DEBUG = False` in settings
- [ ] Configure `ALLOWED_HOSTS` with actual domains
- [ ] Use PostgreSQL instead of SQLite
- [ ] Generate new `SECRET_KEY`
- [ ] Enable HTTPS (`SECURE_SSL_REDIRECT = True`)
- [ ] Configure email backend for notifications
- [ ] Setup S3 or other storage for media files
- [ ] Configure logging and error tracking (Sentry)
- [ ] Run `python manage.py collectstatic`
- [ ] Setup database backups
- [ ] Configure rate limiting

### Production Server Setup

```bash
# Using Gunicorn + Nginx

# Install Gunicorn
pip install gunicorn

# Start server
gunicorn config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  --worker-class sync \
  --timeout 120

# Nginx configuration
server {
    listen 80;
    server_name yourdomain.com;
    
    location /static/ {
        alias /path/to/staticfiles/;
    }
    
    location /media/ {
        alias /path/to/media/;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Project Structure

```
marketplace/
├── config/
│   ├── accounts/          # User management, wallets, auth
│   │   ├── models.py      # User, DealerProfile, Wallets
│   │   ├── views.py       # Auth endpoints
│   │   ├── serializers.py # User serializers
│   │   ├── signals.py     # Auto-create wallets
│   │   └── urls.py
│   ├── admin/             # Admin APIs
│   ├── products/          # Product catalog
│   ├── orders/            # Cart, orders
│   ├── payments/          # Transactions, conversions
│   ├── permissions.py     # Role-based access
│   ├── wallet_utils.py    # Atomic wallet operations
│   ├── settings.py        # Django config
│   ├── urls.py            # Main URL router
│   └── wsgi.py
├── assets/
│   ├── css/               # Tailwind CSS
│   ├── js/                # JavaScript modules
│   └── images/
├── templates/
│   ├── *.html             # Frontend pages
│   └── base-template.html
├── manage.py
└── requirements.txt
```

---

## Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test config.accounts

# With coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

---

## Common Issues & Solutions

### Issue: "Wallet not found" error

**Cause**: User created before signal handler registered

**Solution**:
```bash
python manage.py shell
from config.wallet_utils import WalletManager
from django.contrib.auth import get_user_model
User = get_user_model()
for user in User.objects.all():
    WalletManager.get_or_create_wallets(user)
```

### Issue: Product visible but says "pending review"

**Cause**: Product status is 'pending' instead of 'approved'

**Solution**: Admin must approve via `/api/admin/products/{id}/approve/`

### Issue: Dealer can't upload video

**Cause**: User doesn't have Pro or Enterprise plan

**Solution**: Check subscription status or upgrade plan

---

## Next Steps

### Frontend Enhancements

- [ ] Dealer dashboard with product analytics
- [ ] Advanced search with filters
- [ ] User reviews and ratings
- [ ] Wishlist functionality
- [ ] Order tracking
- [ ] Admin dashboard UI

### Backend Enhancements

- [ ] Email notifications
- [ ] SMS alerts
- [ ] Refund system
- [ ] Dispute resolution
- [ ] Analytics dashboards
- [ ] Automated product expiry

---

## Support

For issues: `support@deepproteam.com`

---

**Built with Django + DRF + Tailwind CSS**
