"""
Dashboard URL Configuration

SECURITY NOTES:
All dashboard views are protected by:
1. @login_required - ensures user is authenticated
2. Custom role-based decorators - ensures user has correct role
3. Return 403 Forbidden if user is not authorized for that role

URL Mapping:
- POST /api/auth../login.html  -> includes redirect_url in response
- GET /admin/dashboard/  -> admin_only view (403 if not admin)
- GET /dealer/dashboard/ -> dealer_only view (403 if not dealer)
- GET /shop/             -> client_only view (403 if not client)
- GET /dashboard/        -> smart redirect based on user role
"""
from django.urls import path
from config.dashboard.views import (
    admin_dashboard,
    dealer_dashboard,
    client_shop,
    dashboard_redirect
)

app_name = 'dashboard'

urlpatterns = [
    path('', dashboard_redirect, name='dashboard'),
    path('admin/', admin_dashboard, name='admin_dashboard'),
    path('dealer/', dealer_dashboard, name='dealer_dashboard'),
    path('shop/', client_shop, name='client_shop'),
]
