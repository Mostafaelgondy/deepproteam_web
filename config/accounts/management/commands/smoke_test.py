from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from config.wallet_utils import WalletManager, CurrencyConverter
from decimal import Decimal


class Command(BaseCommand):
    help = 'Run basic smoke tests for wallets and conversions'

    def handle(self, *args, **options):
        User = get_user_model()
        # Ensure test dealer
        user, created = User.objects.get_or_create(username='qa_dealer', defaults={'email': 'qa_dealer@example.com', 'role': 'dealer'})
        if created:
            user.set_password('qa_pass_123')
            user.save()
            self.stdout.write('Created QA dealer user')

        # Ensure wallets
        egp, gold, mass = WalletManager.get_or_create_wallets(user)
        self.stdout.write(f'Initial balances - EGP: {egp.balance}, Gold: {gold.balance}, Mass: {mass.balance}')

        # Credit EGP
        success, txn, err = WalletManager.add_to_wallet(user, Decimal('500.00'), 'egp', 'QA top-up', transaction_type='test')
        if not success:
            self.stdout.write(self.style.ERROR(f'Failed to credit EGP: {err}'))
            return
        self.stdout.write(self.style.SUCCESS('Credited 500.00 EGP'))

        # Buy Gold with 100 EGP
        success, gold_amount, err = CurrencyConverter.buy_gold(user, Decimal('100.00'))
        if not success:
            self.stdout.write(self.style.ERROR(f'Buy gold failed: {err}'))
        else:
            egp_bal = WalletManager.get_balance(user, 'egp')
            gold_bal = WalletManager.get_balance(user, 'gold')
            self.stdout.write(self.style.SUCCESS(f'Bought Gold: {gold_amount} — New balances EGP: {egp_bal}, Gold: {gold_bal}'))

        # Attempt overdraw
        success, txn, err = WalletManager.deduct_from_wallet(user, Decimal('1000000.00'), 'egp', 'Attempt overdraft', transaction_type='test')
        if not success:
            self.stdout.write(self.style.SUCCESS(f'Overdraw correctly failed: {err}'))
        else:
            self.stdout.write(self.style.ERROR('Overdraw unexpectedly succeeded'))

        self.stdout.write(self.style.SUCCESS('Smoke test completed'))
