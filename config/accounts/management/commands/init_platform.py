"""
Initialize platform with default data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from config.accounts.models import SubscriptionPlan, EGPWallet, GoldWallet, MassWallet
from config.products.models import Category
from config.payments.models import GoldMassConversionRate
from decimal import Decimal

User = get_user_model()


class Command(BaseCommand):
    help = 'Initialize platform with default data'

    def handle(self, *args, **options):
        self.stdout.write('Initializing platform...')
        
        # Create subscription plans
        plans_data = [
            {
                'name': 'starter',
                'price_egp': Decimal('50.00'),
                'max_products': 5,
                'allows_videos': False,
                'ads_enabled': True,
                'duration_days': 30,
                'description': 'Perfect for beginners - list up to 5 products with ads'
            },
            {
                'name': 'pro',
                'price_egp': Decimal('120.00'),
                'max_products': 50,
                'allows_videos': True,
                'ads_enabled': False,
                'duration_days': 30,
                'description': 'Professional plan - list up to 50 products with video support, no ads'
            },
            {
                'name': 'enterprise',
                'price_egp': Decimal('500.00'),
                'max_products': 0,  # Unlimited
                'allows_videos': True,
                'ads_enabled': True,
                'duration_days': 30,
                'description': 'Enterprise plan - unlimited products with video and ads'
            }
        ]
        
        for plan_data in plans_data:
            plan, created = SubscriptionPlan.objects.update_or_create(
                name=plan_data['name'],
                defaults=plan_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created plan: {plan.name}'))
            else:
                self.stdout.write(f'Plan already exists: {plan.name}')
        
        # Create default categories
        categories_data = [
            {'name': 'Electronics', 'slug': 'electronics'},
            {'name': 'Fashion', 'slug': 'fashion'},
            {'name': 'Home & Garden', 'slug': 'home-garden'},
            {'name': 'Sports & Outdoors', 'slug': 'sports-outdoors'},
            {'name': 'Books', 'slug': 'books'},
            {'name': 'Toys & Games', 'slug': 'toys-games'},
            {'name': 'Food & Beverages', 'slug': 'food-beverages'},
            {'name': 'Services', 'slug': 'services'},
        ]
        
        for cat_data in categories_data:
            category, created = Category.objects.update_or_create(
                slug=cat_data['slug'],
                defaults={'name': cat_data['name']}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {category.name}'))
            else:
                self.stdout.write(f'Category already exists: {category.name}')
        
        # Create conversion rates if not exist
        rate, created = GoldMassConversionRate.objects.get_or_create(
            id=1,
            defaults={
                'egp_to_gold': Decimal('10.00'),
                'egp_to_mass': Decimal('5.00'),
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created conversion rates'))
            self.stdout.write(f'1 EGP = {rate.egp_to_gold} Gold = {rate.egp_to_mass} Mass')
        
        # Create admin user if not exists
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@deepproteam.com',
                password='admin123',
                role='admin'
            )
            EGPWallet.objects.get_or_create(user=admin_user, defaults={'balance': Decimal('10000.00')})
            GoldWallet.objects.get_or_create(user=admin_user, defaults={'balance': Decimal('10000.00')})
            MassWallet.objects.get_or_create(user=admin_user, defaults={'balance': Decimal('10000.00')})
            self.stdout.write(self.style.SUCCESS('Created admin user'))
            self.stdout.write('  Username: admin')
            self.stdout.write('  Password: admin123')
        
        self.stdout.write(self.style.SUCCESS('Platform initialized successfully!'))
