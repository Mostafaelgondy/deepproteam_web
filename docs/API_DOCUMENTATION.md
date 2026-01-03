# DeepProTeam Marketplace - Production Ready

A comprehensive, scalable marketplace platform with EGP-based transactions, virtual assets (Gold & Mass), dealer subscription system, and admin panel.

## Technology Stack

- **Frontend**: HTML + Tailwind CSS + Vanilla JavaScript
- **Backend**: Django REST Framework
- **Database**: PostgreSQL (production) / SQLite (development)
- **Authentication**: JWT + Session Management
- **Storage**: File uploads for products, images, and videos

## Currency System

The platform uses three currencies:

1. **EGP (Egyptian Pound)** - Real currency for all transactions
2. **Gold** - Premium virtual credit (1 EGP = 10 Gold)
3. **Mass** - Regular virtual credit (1 EGP = 5 Mass)

## Core Features

### 1. Authentication & Authorization

**Registration**
```
POST /api/auth/register/
{
  "username": "user123",
  "email": "user@example.com",
  "password": "securepass123",
  "password2": "securepass123",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+201001234567",
  "address": "123 Main St",
  "role": "client" or "dealer"
}
```

**Login**
```
POST /api/auth../login.html
{
  "username": "user123",
  "password": "securepass123"
}

Response:
{
  "access": "jwt_token",
  "refresh": "refresh_token",
  "user": {...}
}
```

**Logout**
```
POST /api/auth/logout/
{
  "refresh_token": "refresh_token"
}
```

### 2. Wallet & Balance Management

**Get Wallet Balance**
```
GET /api/auth/wallet/balance/
Response:
{
  "egp": 1000.00,
  "gold": 500.50,
  "mass": 250.25
}
```

### 3. Gold/Mass Shop

**Buy Gold with EGP**
```
POST /api/payments/shop/buy-gold/
{
  "amount_egp": 100
}

Response:
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

**Buy Mass with EGP**
```
POST /api/payments/shop/buy-mass/
{
  "amount_egp": 100
}

Response:
{
  "detail": "Mass purchased successfully",
  "amount_egp": 100,
  "mass_received": 500,
  "new_balances": {...}
}
```

**Get Conversion Rates**
```
GET /api/payments/shop/rates/
Response:
{
  "egp_to_gold": 10,
  "egp_to_mass": 5,
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### 4. Subscription Plans

**List Available Plans**
```
GET /api/auth/subscription/plans/
Response:
[
  {
    "id": 1,
    "name": "starter",
    "price_egp": 50,
    "max_products": 5,
    "allows_videos": false,
    "ads_enabled": true,
    "duration_days": 30,
    "description": "Perfect for beginners..."
  },
  ...
]
```

**Purchase Subscription**
```
POST /api/auth/subscription/purchase/
{
  "plan_id": 1
}

Response:
{
  "detail": "Successfully subscribed to Starter",
  "plan": {...},
  "expires_at": "2024-02-15T10:30:00Z"
}
```

### 5. Product Management

**List All Products**
```
GET /api/shop/products/?search=laptop&category=1
```

**Get Product Details**
```
GET /api/shop/products/{slug}/
Response:
{
  "id": 1,
  "name": "Laptop Pro",
  "slug": "laptop-pro",
  "description": "High-performance laptop",
  "price_egp": 5000,
  "price_gold": 50000,
  "price_mass": 25000,
  "image": "...",
  "video": "...",
  "status": "approved",
  "dealer": "john_dealer",
  "category": {...},
  "reviews": [...],
  "avg_rating": 4.5,
  "review_count": 12
}
```

**Create Product (Dealer)**
```
POST /api/shop/products/
{
  "name": "Laptop Pro",
  "description": "High-performance laptop",
  "category_id": 1,
  "price_egp": 5000,
  "price_gold": 50000,
  "price_mass": 25000,
  "primary_payment_type": "egp",
  "image": <file>,
  "video": <file>,  # Only for Pro/Enterprise plans
  "stock": 10,
  "is_featured": false
}
```

**Update Product**
```
PUT/PATCH /api/shop/products/{slug}/
{...}
```

**Add Product Review**
```
POST /api/shop/products/{slug}/add_review/
{
  "rating": 5,
  "title": "Excellent product",
  "comment": "Really happy with this purchase"
}
```

### 6. Shopping Cart & Orders

**Get Cart**
```
GET /api/orders/cart/
Response:
{
  "id": 1,
  "items": [
    {
      "id": 1,
      "product": {...},
      "quantity": 2,
      "total_price": 10000
    }
  ],
  "total": 10000
}
```

**Add to Cart**
```
POST /api/orders/cart/add_item/
{
  "product_id": 1,
  "quantity": 2
}
```

**Remove from Cart**
```
POST /api/orders/cart/remove_item/
{
  "product_id": 1
}
```

**Create Order from Cart**
```
POST /api/orders/orders/create_from_cart/
{
  "payment_method": "egp",  # "egp", "gold", or "mass"
  "shipping_address": "123 Main St, Cairo",
  "shipping_phone": "+201001234567",
  "notes": "Please handle with care"
}
```

**Process Payment**
```
POST /api/orders/orders/{id}/process_payment/
Response:
{
  "detail": "Payment processed successfully",
  "order": {...}
}
```

**Cancel Order**
```
POST /api/orders/orders/{id}/cancel/
```

### 7. Transaction History

**Get Transactions**
```
GET /api/payments/transactions/?currency=egp&status=completed
Response:
[
  {
    "id": 1,
    "transaction_type": "purchase",
    "currency": "egp",
    "amount": 500,
    "status": "completed",
    "description": "Order #123",
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

### 8. Dealer Profile

**Get Dealer Profile**
```
GET /api/auth/dealer/profile/
Response:
{
  "business_name": "John's Shop",
  "subscription_plan": {...},
  "subscription_start_date": "2024-01-15T10:30:00Z",
  "subscription_end_date": "2024-02-15T10:30:00Z",
  "products_published": 3,
  "has_used_free_product": true,
  "rating": 4.8,
  "total_sales": 15000,
  "can_publish": true,
  "is_subscription_active": true
}
```

**Update Dealer Profile**
```
PATCH /api/auth/dealer/profile/
{
  "business_name": "John's Electronics Store",
  "business_description": "Premium electronics and gadgets"
}
```

### 9. Admin APIs

**Manage Users**
```
GET /api/admin/users/
PATCH /api/admin/users/{id}/approve_dealer/
POST /api/admin/users/{id}/suspend_user/ {reason: "..."}
POST /api/admin/users/{id}/activate_user/
```

**Manage Dealers**
```
GET /api/admin/dealers/
POST /api/admin/dealers/{id}/change_subscription/
{
  "plan_id": 1
}
```

**Product Moderation**
```
GET /api/admin/products/?status=pending
POST /api/admin/products/{id}/approve/
POST /api/admin/products/{id}/reject/ {reason: "..."}
POST /api/admin/products/{id}/suspend/ {reason: "..."}
```

**Financial Reports**
```
GET /api/admin/reports/financial/?from_date=2024-01-01&to_date=2024-01-31
Response:
{
  "period": {...},
  "revenue": {
    "egp": 50000,
    "gold": 100000,
    "mass": 50000
  },
  "transactions": {
    "count": 150,
    "by_type": {...}
  },
  "orders": {...},
  "users": {...}
}
```

**Conversion Rates**
```
GET /api/admin/conversion-rates/
PATCH /api/admin/conversion-rates/
{
  "egp_to_gold": 10,
  "egp_to_mass": 5
}
```

## Business Rules

### Subscription Rules
1. **First Product is FREE** - Every dealer gets one free product listing
2. **Subsequent Products Require Subscription** - After the first product, dealers must maintain an active subscription
3. **Plan Limits** are enforced:
   - Starter: 5 products max
   - Pro: 50 products max
   - Enterprise: Unlimited products
4. **Video Uploads** only allowed for Pro and Enterprise plans

### Payment & Transactions
1. All prices can be set in EGP, Gold, or Mass
2. Customers can pay in any currency they have balance for
3. All transactions are atomic and protected against race conditions
4. Refunds are automatically credited to the original currency

### Product Moderation
1. All products start as "pending" review
2. Admin can approve, reject, or suspend products
3. Only approved products appear in public listings
4. Products auto-expire after listing duration

## Setup Instructions

### Requirements
- Python 3.9+
- PostgreSQL 12+ (for production)
- Node.js 16+ (optional, for frontend tooling)

### Installation

```bash
# Clone repository
git clone <repo_url>
cd marketplace

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DJANGO_SECRET_KEY='your-secret-key'
export DJANGO_DEBUG=False
export DB_NAME=marketplace
export DB_USER=postgres
export DB_PASSWORD=password
export DB_HOST=localhost
export DB_PORT=5432

# Run migrations
python manage.py migrate

# Initialize platform with default data
python manage.py init_platform

# Create superuser (optional, init_platform creates admin)
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### Environment Variables
```
DJANGO_SECRET_KEY=<random-secret-key>
DJANGO_DEBUG=True|False
DB_NAME=marketplace
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432
FRONTEND_URL=http://localhost:8000
DEFAULT_FROM_EMAIL=noreply@marketplace.com
```

## Security Considerations

1. **CSRF Protection** - All POST requests require CSRF token
2. **Password Security** - Minimum 8 characters, hashed with Django's password hasher
3. **JWT Tokens** - Short-lived access tokens (60 minutes), long-lived refresh tokens (1 day)
4. **Role-Based Access** - Backend enforces all permissions, not frontend
5. **Atomic Transactions** - Database locks prevent wallet race conditions
6. **SQL Injection Protection** - Django ORM with parameterized queries
7. **Rate Limiting** - Recommended to add on production
8. **HTTPS Only** - Set `SECURE_SSL_REDIRECT=True` in production

## Deployment

### Production Checklist
1. Set `DEBUG=False`
2. Configure allowed hosts
3. Use PostgreSQL instead of SQLite
4. Set secure SECRET_KEY
5. Enable HTTPS
6. Configure email backend
7. Set up error logging (Sentry, etc.)
8. Configure media file storage (S3, etc.)
9. Run `python manage.py collectstatic`
10. Use a production WSGI server (Gunicorn, etc.)

### Gunicorn Example
```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

## API Response Format

All API responses follow this format:

**Success (2xx)**
```json
{
  "data": {...},
  "message": "Success message",
  "errors": null
}
```

**Error (4xx, 5xx)**
```json
{
  "data": null,
  "message": "Error message",
  "errors": {
    "field": ["error details"]
  }
}
```

## File Structure

```
marketplace/
├── config/
│   ├── accounts/          # User management, wallets
│   ├── admin/             # Admin APIs
│   ├── products/          # Product catalog
│   ├── orders/            # Cart, orders
│   ├── payments/          # Transactions, conversions
│   ├── permissions.py     # Role-based access control
│   ├── wallet_utils.py    # Atomic wallet operations
│   └── settings.py        # Django configuration
├── assets/
│   ├── css/
│   ├── js/
│   └── images/
├── [html files]/          # Frontend templates
├── manage.py
└── requirements.txt
```

## Testing

```bash
# Run tests
python manage.py test

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## Support

For issues and questions, contact: support@deepproteam.com

## License

Proprietary - DeepProTeam 2024
