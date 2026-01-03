"""
Custom permission classes for role-based access control
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from rest_framework.permissions import BasePermission, IsAuthenticated


def is_admin_user(user):
    """Return True if the user should be considered an admin.

    Prefer Django's `is_staff`/`is_superuser` flags, fall back to legacy
    `role == 'admin'` when present.
    """
    if not user or user.is_anonymous:
        return False
    return bool(getattr(user, 'is_staff', False) or getattr(user, 'is_superuser', False) or getattr(user, 'role', None) == 'admin')


def admin_only(view_func):
    """Decorator: Allow only authenticated admin users"""
    @wraps(view_func)
    @login_required(login_url='login')
    def wrapped_view(request, *args, **kwargs):
        # Prefer Django's built-in staff/superuser flags for admin-level checks.
        if not (getattr(request.user, 'is_staff', False) or getattr(request.user, 'is_superuser', False) or getattr(request.user, 'role', None) == 'admin'):
            return HttpResponseForbidden('Access denied. Admin privileges required.')
        return view_func(request, *args, **kwargs)
    return wrapped_view


def dealer_only(view_func):
    """Decorator: Allow only authenticated dealer users"""
    @wraps(view_func)
    @login_required(login_url='login')
    def wrapped_view(request, *args, **kwargs):
        if request.user.role != 'dealer':
            return HttpResponseForbidden('Access denied. Dealer privileges required.')
        return view_func(request, *args, **kwargs)
    return wrapped_view


def client_only(view_func):
    """Decorator: Allow only authenticated client users"""
    @wraps(view_func)
    @login_required(login_url='login')
    def wrapped_view(request, *args, **kwargs):
        if request.user.role != 'client':
            return HttpResponseForbidden('Access denied. Client privileges required.')
        return view_func(request, *args, **kwargs)
    return wrapped_view


class IsAdmin(IsAuthenticated):
    """Allow access only to admin users"""
    def has_permission(self, request, view):
        # Use Django's `is_staff`/`is_superuser` flags for robust admin checks,
        # keep legacy `role == 'admin'` as fallback for earlier user models.
        if not super().has_permission(request, view):
            return False
        user = request.user
        return bool(getattr(user, 'is_staff', False) or getattr(user, 'is_superuser', False) or getattr(user, 'role', None) == 'admin')


class IsDealer(IsAuthenticated):
    """Allow access only to dealer users"""
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return getattr(request.user, 'role', None) == 'dealer'


class IsClient(IsAuthenticated):
    """Allow access only to client users"""
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return getattr(request.user, 'role', None) == 'client'


class IsApprovedDealer(IsDealer):
    """Allow access only to approved dealers"""
    def has_permission(self, request, view):
        return (
            super().has_permission(request, view) and
            request.user.is_approved
        )


class IsOwnerOrAdmin(BasePermission):
    """Allow access to owner of object or admin"""
    def has_object_permission(self, request, view, obj):
        # Allow if user is admin
        user = request.user
        if bool(getattr(user, 'is_staff', False) or getattr(user, 'is_superuser', False) or getattr(user, 'role', None) == 'admin'):
            return True
        
        # Check if user is owner
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'dealer'):
            return obj.dealer == request.user
        
        return False


class IsDealerOwner(BasePermission):
    """Allow access only to dealer who owns the product"""
    def has_object_permission(self, request, view, obj):
        user = request.user
        if bool(getattr(user, 'is_staff', False) or getattr(user, 'is_superuser', False) or getattr(user, 'role', None) == 'admin'):
            return True
        return getattr(obj, 'dealer', None) == user


class IsAuthenticatedOrReadOnly(BasePermission):
    """Allow read access to anyone, write access only to authenticated users"""
    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return request.user and request.user.is_authenticated
