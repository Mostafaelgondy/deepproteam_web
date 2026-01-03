"""
Django signals for automatic initialization
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from config.accounts.models import EGPWallet, GoldWallet, MassWallet, DealerProfile
from decimal import Decimal

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_wallets(sender, instance, created, **kwargs):
    """Create wallets when user is created"""
    if created:
        EGPWallet.objects.get_or_create(user=instance)
        GoldWallet.objects.get_or_create(user=instance)
        MassWallet.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def create_dealer_profile(sender, instance, created, **kwargs):
    """Create dealer profile when dealer user is created"""
    if created and instance.role == 'dealer':
        DealerProfile.objects.get_or_create(user=instance)
