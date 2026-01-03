"""
URL configuration for config project.

SECURITY ARCHITECTURE:
- All dashboard URLs require authentication via @login_required decorator
- Role-based access enforced via custom decorators (@admin_only, @dealer_only, @client_only)
- Admin dashboards return 403 Forbidden if accessed by non-admin users
- Direct static file access to dashboards is disabled
- Login endpoint returns redirect_url based on user.role for correct post-login navigation
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from config.dashboard.views import dashboard_redirect


urlpatterns = [
    # Root path → redirect based on role
    path('', dashboard_redirect, name='dashboard-redirect'),

    # Django admin
    path('admin-django/', admin.site.urls),

    # Dashboards
    path('admin/dashboard/', include('config.dashboard.urls')),
    path('dealer/dashboard/', include('config.dashboard.urls')),
    path('shop/', include('config.dashboard.urls')),
    path('dashboard/', include('config.dashboard.urls')),

    # API endpoints
    path('api/auth/', include('config.accounts.urls')),
    path('api/shop/', include('config.products.urls')),
    path('api/orders/', include('config.orders.urls')),
    path('api/payments/', include('config.payments.urls')),
    path('api/admin/', include('config.admin.urls')),
    path('api/support/', include('config.support.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
