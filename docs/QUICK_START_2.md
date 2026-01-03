# Quick Start Guide

## ⚡ Get the Marketplace Running in 3 Steps

### Step 1: Seed Test Data (30 seconds)
```bash
cd "e:/Own_work/Business/DeepProTeam/try 5/Market_place"
python manage.py seed_test_data
```

Output:
```
✓ Admin user created
✓ Dealer user created
✓ Client user created
✓ Categories created
✓ Products created

✅ Test data seeded successfully!

Test Credentials:
Admin:  username=admin, password=admin123
Dealer: username=dealer1, password=dealer123
Client: username=client1, password=client123
```

### Step 2: Start the Server (5 seconds)
```bash
python manage.py runserver
```

Server runs at: `http://localhost:8000`

### Step 3: Run End-to-End Test (2 seconds)
```bash
# In another terminal
python e2e_test.py
```

Expected output:
```
✅ E2E TEST PASSED
Successfully completed marketplace flow:
  1. Authenticated user: client1
  2. Added product to cart: Cloud Backup
  3. Created order with tax: EGP 207.90
  4. Processed payment via mock gateway
  5. Deducted from wallet: EGP 207.90
  6. Order status changed to: paid
```

---

## 🎯 What You Can Do Now

### As an Admin
```bash
# Login
curl -X POST http://localhost:8000/api/auth../login.html \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# List all users
curl http://localhost:8000/api/admin/users/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# Approve a product
curl -X POST http://localhost:8000/api/admin/products/1/approve/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# Get financial report
curl "http://localhost:8000/api/admin/reports/financial/" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

### As a Dealer
```bash
# Create a product
curl -X POST http://localhost:8000/api/shop/products/ \
  -H "Authorization: Bearer $DEALER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Service",
    "description": "...",
    "price_egp": 499,
    "category_id": 1,
    "stock": 10
  }'

# View your products
curl http://localhost:8000/api/shop/products/my_products/ \
  -H "Authorization: Bearer $DEALER_TOKEN"
```

### As a Client
```bash
# Browse products
curl http://localhost:8000/api/shop/products/

# Add to cart
curl -X POST http://localhost:8000/api/orders/cart/add_item/ \
  -H "Authorization: Bearer $CLIENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"product_id": 1, "quantity": 1}'

# Checkout
curl -X POST http://localhost:8000/api/orders/orders/create_from_cart/ \
  -H "Authorization: Bearer $CLIENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "payment_method": "egp",
    "shipping_address": "123 Main St",
    "shipping_phone": "+201234567890"
  }'

# Pay for order
curl -X POST http://localhost:8000/api/orders/orders/1/process_payment/ \
  -H "Authorization: Bearer $CLIENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

---

## 📚 Documentation

- **[MARKETPLACE_GUIDE.md](MARKETPLACE_GUIDE.md)** - Complete guide with all endpoints
- **[docs/ADMIN_CONTROL.md](docs/ADMIN_CONTROL.md)** - Admin system documentation
- **[IMPROVEMENTS_SUMMARY.md](IMPROVEMENTS_SUMMARY.md)** - What was fixed

---

## ✅ What's Working

- ✅ User registration & login (JWT auth)
- ✅ Product catalog with search & filtering
- ✅ Shopping cart with add/remove/clear
- ✅ Checkout with tax calculation (5%)
- ✅ Wallet system (EGP, Gold, Mass)
- ✅ Payment processing (mock gateway, ready for real)
- ✅ Order management & history
- ✅ Admin control (user approval, product moderation)
- ✅ Financial reports
- ✅ Subscription plans for dealers
- ✅ Product reviews & ratings

---

## 🔧 Admin Panel

### Django Admin
```
http://localhost:8000/admin-django/
Username: admin
Password: admin123
```

Manage:
- Users (create, edit, delete)
- Products (list, view details)
- Orders (view, cancel)
- Wallets (view balances)
- Transactions (audit trail)

### Admin API Dashboard
```
http://localhost:8000/admin/dashboard/
```

View:
- Platform statistics
- Recent activity logs
- User approvals
- Product moderation queue

---

## 🚀 Deploying to Production

1. **Update settings**:
   ```python
   # config/settings.py
   DEBUG = False
   SECRET_KEY = 'your-secret-key-from-env'
   ALLOWED_HOSTS = ['your-domain.com']
   SECURE_SSL_REDIRECT = True
   ```

2. **Run migrations**:
   ```bash
   python manage.py migrate --noinput
   ```

3. **Create admin user**:
   ```bash
   python manage.py createsuperuser
   ```

4. **Collect static files**:
   ```bash
   python manage.py collectstatic --no-input
   ```

5. **Start with gunicorn**:
   ```bash
   gunicorn config.wsgi:application
   ```

---

## ⚠️ Common Issues

**Q: "Password does not match" on login**
- A: Use the exact credentials from the seed output (admin123, dealer123, client123)

**Q: "Insufficient balance" on checkout**
- A: Test users have pre-funded wallets. For new users, add funds via the API or admin panel.

**Q: Admin endpoints return 403**
- A: Make sure you're logged in as admin user (created with `createsuperuser`)

**Q: E2E test fails**
- A: Make sure you ran `python manage.py seed_test_data` first

---

## 📊 System Status

| Component | Status | Location |
|-----------|--------|----------|
| Authentication | ✅ Working | `/api/auth/` |
| Products | ✅ Working | `/api/shop/` |
| Shopping Cart | ✅ Working | `/api/orders/cart/` |
| Checkout | ✅ Working | `/api/orders/orders/create_from_cart/` |
| Payments | ✅ Working | `/api/orders/orders/{id}/process_payment/` |
| Admin Control | ✅ Working | `/api/admin/` |
| Wallets | ✅ Working | `/api/auth/wallet/balance/` |
| Reports | ✅ Working | `/api/admin/reports/financial/` |

---

## 🎓 Learning Path

1. **Understand the flow**: Read [MARKETPLACE_GUIDE.md](MARKETPLACE_GUIDE.md)
2. **Run the E2E test**: `python e2e_test.py` (validates everything)
3. **Test manually**: Use curl commands above or a tool like Postman
4. **Review the code**: Check [config/orders/views.py](config/orders/views.py) for checkout logic
5. **Explore admin**: Login to Django admin at `/admin-django/`
6. **Deploy**: Follow production steps when ready

---

## ✨ You're All Set!

The marketplace is fully functional with:
- Real admin control (not fake checks)
- Complete checkout flow with tax
- Mock payment gateway (ready to swap with Stripe)
- Full end-to-end testing
- Production-ready code

**Start here**: `python manage.py runserver` and visit `http://localhost:8000`

Questions? See [MARKETPLACE_GUIDE.md](MARKETPLACE_GUIDE.md) or [docs/ADMIN_CONTROL.md](docs/ADMIN_CONTROL.md).
