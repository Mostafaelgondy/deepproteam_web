from django.urls import path, include
from rest_framework.routers import DefaultRouter
from config.admin.views import (
    AdminUserManagementViewSet,
    AdminDealerManagementViewSet,
    AdminProductModerationViewSet,
    AdminFinancialReportView,
    AdminConversionRateView
)

router = DefaultRouter()
router.register(r'users', AdminUserManagementViewSet, basename='admin-users')
router.register(r'dealers', AdminDealerManagementViewSet, basename='admin-dealers')
router.register(r'products', AdminProductModerationViewSet, basename='admin-products')

urlpatterns = [
    path('', include(router.urls)),
    path('reports/financial/', AdminFinancialReportView.as_view(), name='financial_reports'),
    path('conversion-rates/', AdminConversionRateView.as_view(), name='conversion_rates'),
]
