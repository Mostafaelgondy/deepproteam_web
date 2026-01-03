from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from config.permissions import admin_only, dealer_only, client_only, is_admin_user


@admin_only
def admin_dashboard(request):
    """Admin dashboard - only accessible by admin users"""
    context = {
        'user': request.user,
    }
    return render(request, 'admin/dashboard-admin.html', context)


@dealer_only
def dealer_dashboard(request):
    """Dealer dashboard - only accessible by dealer users"""
    dealer_profile = None
    if hasattr(request.user, 'dealer_profile'):
        dealer_profile = request.user.dealer_profile
    
    context = {
        'user': request.user,
        'dealer_profile': dealer_profile,
    }
    return render(request, 'dealer/dashboard.html', context)


@client_only
def client_shop(request):
    """Client shop - only accessible by client users"""
    context = {
        'user': request.user,
    }
    return render(request, 'client/shop.html', context)


@login_required(login_url='login')
def dashboard_redirect(request):
    """Smart redirect based on user role"""
    if is_admin_user(request.user):
        return redirect('admin_dashboard')
    elif getattr(request.user, 'role', None) == 'dealer':
        return redirect('dealer_dashboard')
    else:
        return redirect('client_shop')
