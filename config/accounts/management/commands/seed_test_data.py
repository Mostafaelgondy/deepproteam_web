"""
Management command to seed database with test data for development.
Usage: python manage.py seed_test_data
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from decimal import Decimal
from config.accounts.models import DealerProfile, SubscriptionPlan, EGPWallet, GoldWallet, MassWallet
from config.products.models import Category, Product

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed database with test data for development and E2E testing'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Seeding test data...'))
        
        # Helper to initialize wallets
        def init_wallets(user, egp=Decimal('0'), gold=Decimal('0'), mass=Decimal('0')):
            if egp > 0:
                w, _ = EGPWallet.objects.get_or_create(user=user)
                w.balance = egp
                w.save()
            if gold > 0:
                w, _ = GoldWallet.objects.get_or_create(user=user)
                w.balance = gold
                w.save()
            if mass > 0:
                w, _ = MassWallet.objects.get_or_create(user=user)
                w.balance = mass
                w.save()
        
        # Create admin user
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@deepproteam.com',
                password='admin123',
                role='admin'
            )
            admin.is_staff = True
            admin.is_superuser = True
            admin.save()
            init_wallets(admin, Decimal('10000'), Decimal('1000'), Decimal('500'))
            self.stdout.write(self.style.SUCCESS('✓ Admin user created'))
        
        # Create dealer user
        if not User.objects.filter(username='dealer1').exists():
            dealer = User.objects.create_user(
                username='dealer1',
                email='dealer1@deepproteam.com',
                password='dealer123',
                role='dealer',
                is_approved=True
            )
            init_wallets(dealer, Decimal('5000'), Decimal('500'), Decimal('200'))
            
            # Create dealer profile
            plan = SubscriptionPlan.objects.filter(is_active=True).first()
            DealerProfile.objects.create(
                user=dealer,
                store_name='TechNova Store',
                subscription_plan=plan
            )
            self.stdout.write(self.style.SUCCESS('✓ Dealer user created'))
        
        # Create client user
        if not User.objects.filter(username='client1').exists():
            client = User.objects.create_user(
                username='client1',
                email='client1@deepproteam.com',
                password='client123',
                role='client'
            )
            init_wallets(client, Decimal('2000'), Decimal('100'), Decimal('50'))
            self.stdout.write(self.style.SUCCESS('✓ Client user created'))
        
        # Create categories
        categories_data = [
            ('Electronics', 'electronics'),
            ('Software', 'software'),
            ('Services', 'services'),
            ('Courses', 'courses'),
        ]
        
        for name, slug in categories_data:
            if not Category.objects.filter(slug=slug).exists():
                Category.objects.create(
                    name=name,
                    slug=slug,
                    is_active=True
                )
        self.stdout.write(self.style.SUCCESS('✓ Categories created'))
        
        # Create products
        dealer = User.objects.get(username='dealer1')
        category = Category.objects.first()
        
        products_data = [
            ('Laptop Pro', 'laptop-pro', 'High-performance laptop for development', Decimal('5999')),
            ('Python Course', 'python-course', 'Complete Python programming course', Decimal('299')),
            ('Web Design Service', 'web-design', 'Professional web design service', Decimal('1999')),
            ('Cloud Backup', 'cloud-backup', '1TB Cloud backup service', Decimal('99')),
        ]
        
        for name, slug, desc, price in products_data:
            if not Product.objects.filter(slug=slug).exists():
                Product.objects.create(
                    dealer=dealer,
                    name=name,
                    slug=slug,
                    description=desc,
                    price_egp=price,
                    price_gold=price / Decimal('100'),
                    category=category,
                    status='approved',
                    stock=100
                )
        self.stdout.write(self.style.SUCCESS('✓ Products created'))
        
        self.stdout.write(self.style.SUCCESS('\n✅ Test data seeded successfully!'))
        self.stdout.write(self.style.WARNING('\nTest Credentials:'))
        self.stdout.write('Admin:  username=admin, password=admin123')
        self.stdout.write('Dealer: username=dealer1, password=dealer123')
        self.stdout.write('Client: username=client1, password=client123')
        self.stdout.write('\nWallets pre-funded for testing checkout flow.')
