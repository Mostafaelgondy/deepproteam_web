# DeepProTeam Marketplace - Admin Control & Security

## Overview

This document describes the real, production-ready admin control system in the DeepProTeam Marketplace. The system uses Django's native `is_staff` and `is_superuser` flags as the primary admin indicators, with fallback support for a legacy custom `role='admin'` field for backwards compatibility.

---

## Admin Authentication & Authorization

### 1. Creating Admin Users

#### Via Django Admin Shell
```bash
python manage.py shell
```

```python
from django.contrib.auth import get_user_model
User = get_user_model()

# Create superuser (highest privilege)
admin = User.objects.create_superuser(
    username='admin_user',
    email='admin@deepproteam.com',
    password='secure_password',
    role='admin'  # Legacy field, optional
)
# is_staff and is_superuser are set automatically

# Create staff user (moderate privilege)
staff = User.objects.create_user(
    username='staff_user',
    email='staff@deepproteam.com',
    password='secure_password',
    role='admin',
    is_staff=True
)
staff.save()
```

#### Via Django Management Command
```bash
python manage.py createsuperuser
# Follow prompts to set username, email, password
# Then set role='admin' manually if desired
```

### 2. Admin Permission Checks (Server-Side)

All permission checks use the centralized **`is_admin_user(user)`** helper in `config/permissions.py`:

```python
from config.permissions import is_admin_user

if is_admin_user(request.user):
    # User is admin: check passed
```

This function checks in order:
1. `user.is_staff` (Django native)
2. `user.is_superuser` (Django native)
3. `user.role == 'admin'` (legacy fallback)

**Why this approach?**
- Leverages Django's built-in permission framework
- Ensures compatibility with Django admin panel (`/admin-django/`)
- Allows gradual migration from custom role field to standard Django auth
- Prevents attribute errors if `role` field is missing

### 3. Admin Permission Classes (DRF)

The **`IsAdmin`** permission class is used for API endpoints:

```python
from rest_framework import permissions
from config.permissions import IsAdmin

class AdminViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin]  # Note: class, not instance
```

This enforces:
- User must be authenticated
- User must have `is_staff`, `is_superuser`, or `role='admin'`

---

## Admin Endpoints

### User Management
```
GET/POST   /api/admin/users/                    - List/create users
GET/PUT    /api/admin/users/{id}/               - Retrieve/update user
DELETE     /api/admin/users/{id}/               - Delete user
POST       /api/admin/users/{id}/approve_dealer/  - Approve dealer account
POST       /api/admin/users/{id}/suspend_user/   - Suspend user account
POST       /api/admin/users/{id}/activate_user/  - Reactivate user
```

### Dealer Management
```
GET/POST   /api/admin/dealers/                         - List/create dealers
GET/PUT    /api/admin/dealers/{id}/                    - Retrieve/update dealer
POST       /api/admin/dealers/{id}/change_subscription/ - Change subscription plan
```

### Product Moderation
```
GET        /api/admin/products/              - List all products (pending, approved, rejected)
POST       /api/admin/products/{id}/approve/ - Approve product for listing
POST       /api/admin/products/{id}/reject/  - Reject product with reason
POST       /api/admin/products/{id}/suspend/ - Suspend product listing
```

### Financial Reports
```
GET        /api/admin/reports/financial/     - Revenue, user stats, transaction breakdown
  Query params:
    - from_date (ISO format, default: 30 days ago)
    - to_date   (ISO format, default: today)
```

### Conversion Rates
```
GET/PUT    /api/conversion-rates/            - Get/update Gold↔Mass conversion rates
```

---

## Admin Dashboard (Frontend)

The admin dashboard at `/admin/dashboard-admin.html` enforces real admin checks:

### Real Authentication Flow
1. User logs in via `/api/auth../login.html` → receives JWT token
2. Token stored in `localStorage` as `access`
3. Dashboard calls `/api/auth/me/` with token
4. Backend validates user is admin
5. If not admin → redirect to login

**Relevant code:**
- [assets/js/admin/admin.dashboard.js](assets/js/admin/admin.dashboard.js#L1-L100)

```javascript
// Real permission check (not hardcoded)
const isAdmin = Boolean(user.is_staff || user.is_superuser || user.role === 'admin');
if (!isAdmin) {
    window.location.href = '../../login.html';
}
```

---

## Security Features

### 1. CSRF Protection
- All POST/PUT/DELETE requests require CSRF token
- Enabled via `CsrfViewMiddleware` in settings.py

### 2. Session Timeout
- JWT tokens expire after 60 minutes
- Refresh tokens valid for 24 hours
- Blacklist prevents token reuse after logout

### 3. Role Isolation
- Decorators enforce role-based access (`@admin_only`, `@dealer_only`, `@client_only`)
- ViewSet permission classes block unauthorized requests
- Object-level permissions prevent users from accessing other users' data

### 4. Audit Trail
- All transactions logged in `Transaction` model
- User actions tracked with timestamps
- Product reviews marked as verified purchases

### 5. Input Validation
- Serializers validate all incoming data
- Quantity, price, amount fields are type-checked
- Email addresses validated
- Weak password rejection

---

## Django Admin Panel

Access the native Django admin panel at `/admin-django/`:

1. Login with superuser credentials
2. Manage:
   - Users (create, edit, delete)
   - Wallets (view balances, adjust manually for testing)
   - Products (approve, reject, suspend)
   - Orders (view, cancel)
   - Transactions (audit trail)

---

## Testing Admin Controls

### Test Data
Run the seed command to create test users:

```bash
python manage.py seed_test_data
```

This creates:
- **Admin**: `admin` / `admin123` (superuser with full wallets)
- **Dealer**: `dealer1` / `dealer123` (approved dealer with store)
- **Client**: `client1` / `client123` (buyer with funds)

### Manual Testing
```bash
# 1. Login as admin
curl -X POST http://localhost:8000/api/auth../login.html \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 2. Save the access token
ACCESS_TOKEN=<token_from_response>

# 3. List all users (admin only)
curl -H "Authorization: Bearer $ACCESS_TOKEN" \
  http://localhost:8000/api/admin/users/

# 4. Approve a dealer
curl -X POST \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  http://localhost:8000/api/admin/users/2/approve_dealer/

# 5. Suspend a user
curl -X POST \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"reason":"Suspicious activity"}' \
  http://localhost:8000/api/admin/users/3/suspend_user/
```

---

## Extending Admin Permissions

### Adding Custom Permissions
```python
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from config.products.models import Product

# Create custom permission
content_type = ContentType.objects.get_for_model(Product)
permission = Permission.objects.create(
    codename='can_bulk_approve',
    name='Can bulk approve products',
    content_type=content_type,
)

# Assign to user
user.user_permissions.add(permission)
```

### Using Custom Permissions in Views
```python
from rest_framework.permissions import BasePermission

class CanBulkApprove(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('products.can_bulk_approve')

class ProductBulkViewSet(viewsets.ViewSet):
    permission_classes = [IsAdmin, CanBulkApprove]
```

---

## Migration from Custom Roles to Django Permissions

**Legacy approach (deprecated):**
```python
if request.user.role == 'admin':  # ❌ Avoid this
    ...
```

**New approach (recommended):**
```python
if is_admin_user(request.user):  # ✓ Use this
    ...
```

The `is_admin_user()` helper handles the transition seamlessly. Over time, remove references to `role='admin'` and rely solely on `is_staff`/`is_superuser`.

---

## Production Checklist

- [ ] Set `DEBUG = False` in `config/settings.py`
- [ ] Use strong `SECRET_KEY` from environment
- [ ] Enable `SECURE_HSTS_SECONDS` and HTTPS
- [ ] Set `CSRF_COOKIE_SECURE = True`
- [ ] Configure email backend for real SMTP
- [ ] Set up database backups
- [ ] Enable admin activity logging
- [ ] Configure rate limiting on auth endpoints
- [ ] Set up monitoring/alerting for admin actions
- [ ] Audit user permissions regularly
- [ ] Use environment variables for all secrets

---

## Troubleshooting

**Issue:** Admin endpoints return 403 Forbidden
- **Cause:** User is not marked as `is_staff` or `is_superuser`
- **Solution:** `user.is_staff = True; user.save()` or use `create_superuser`

**Issue:** JWT token expired
- **Cause:** Access token lifetime exceeded (default: 60 min)
- **Solution:** Use refresh token to get new access token
```bash
curl -X POST http://localhost:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh":"<refresh_token>"}'
```

**Issue:** Permission denied on specific object
- **Cause:** Object-level permission check failed
- **Solution:** Check `IsOwnerOrAdmin` permission; only owner or admin can modify

---

## Related Files

- Permission classes: [config/permissions.py](config/permissions.py)
- Admin views: [config/admin/views.py](config/admin/views.py)
- Admin URLs: [config/admin/urls.py](config/admin/urls.py)
- Dashboard frontend: [assets/js/admin/admin.dashboard.js](assets/js/admin/admin.dashboard.js)
- Settings: [config/settings.py](config/settings.py) (JWT, CORS, etc.)
