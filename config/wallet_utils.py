"""
Wallet and transaction utilities with atomic operations
"""
from django.db import transaction, IntegrityError
from django.db.models import F
from django.core.cache import cache
from decimal import Decimal
from config.accounts.models import User, EGPWallet, GoldWallet, MassWallet
from config.payments.models import Transaction, GoldMassConversionRate


class WalletManager:
    """Manages wallet operations atomically"""
    
    @staticmethod
    def get_or_create_wallets(user):
        """Ensure user has all wallets"""
        egp_wallet, _ = EGPWallet.objects.get_or_create(user=user)
        gold_wallet, _ = GoldWallet.objects.get_or_create(user=user)
        mass_wallet, _ = MassWallet.objects.get_or_create(user=user)
        return egp_wallet, gold_wallet, mass_wallet
    
    @staticmethod
    def get_balance(user, currency):
        """Get wallet balance for a currency"""
        if currency == 'egp':
            wallet, _ = EGPWallet.objects.get_or_create(user=user)
            return wallet.balance
        elif currency == 'gold':
            wallet, _ = GoldWallet.objects.get_or_create(user=user)
            return wallet.balance
        elif currency == 'mass':
            wallet, _ = MassWallet.objects.get_or_create(user=user)
            return wallet.balance
        return Decimal('0.00')
    
    @staticmethod
    @transaction.atomic
    def deduct_from_wallet(user, amount, currency, description, transaction_type='purchase', **kwargs):
        """
        Deduct from wallet atomically.
        Returns: (success: bool, transaction: Transaction or None, error: str or None)
        """
        try:
            if currency == 'egp':
                wallet = EGPWallet.objects.select_for_update().get(user=user)
                if wallet.balance < amount:
                    return False, None, f"Insufficient EGP balance. Required: {amount}, Available: {wallet.balance}"
                wallet.balance = F('balance') - amount
                wallet.save(update_fields=['balance', 'updated_at'])
            
            elif currency == 'gold':
                wallet = GoldWallet.objects.select_for_update().get(user=user)
                if wallet.balance < amount:
                    return False, None, f"Insufficient Gold balance. Required: {amount}, Available: {wallet.balance}"
                wallet.balance = F('balance') - amount
                wallet.save(update_fields=['balance', 'updated_at'])
            
            elif currency == 'mass':
                wallet = MassWallet.objects.select_for_update().get(user=user)
                if wallet.balance < amount:
                    return False, None, f"Insufficient Mass balance. Required: {amount}, Available: {wallet.balance}"
                wallet.balance = F('balance') - amount
                wallet.save(update_fields=['balance', 'updated_at'])
            
            else:
                return False, None, f"Invalid currency: {currency}"
            
            # Create transaction record
            txn = Transaction.objects.create(
                user=user,
                transaction_type=transaction_type,
                currency=currency,
                amount=amount,
                description=description,
                status='completed',
                **kwargs
            )
            
            return True, txn, None
        
        except EGPWallet.DoesNotExist:
            return False, None, "EGP wallet not found"
        except GoldWallet.DoesNotExist:
            return False, None, "Gold wallet not found"
        except MassWallet.DoesNotExist:
            return False, None, "Mass wallet not found"
        except Exception as e:
            return False, None, str(e)
    
    @staticmethod
    @transaction.atomic
    def add_to_wallet(user, amount, currency, description, transaction_type='purchase', **kwargs):
        """
        Add to wallet atomically.
        Returns: (success: bool, transaction: Transaction or None, error: str or None)
        """
        try:
            if currency == 'egp':
                wallet = EGPWallet.objects.select_for_update().get(user=user)
                wallet.balance = F('balance') + amount
                wallet.save(update_fields=['balance', 'updated_at'])
            
            elif currency == 'gold':
                wallet = GoldWallet.objects.select_for_update().get(user=user)
                wallet.balance = F('balance') + amount
                wallet.save(update_fields=['balance', 'updated_at'])
            
            elif currency == 'mass':
                wallet = MassWallet.objects.select_for_update().get(user=user)
                wallet.balance = F('balance') + amount
                wallet.save(update_fields=['balance', 'updated_at'])
            
            else:
                return False, None, f"Invalid currency: {currency}"
            
            # Create transaction record
            txn = Transaction.objects.create(
                user=user,
                transaction_type=transaction_type,
                currency=currency,
                amount=amount,
                description=description,
                status='completed',
                **kwargs
            )
            
            return True, txn, None
        
        except (EGPWallet.DoesNotExist, GoldWallet.DoesNotExist, MassWallet.DoesNotExist) as e:
            return False, None, f"Wallet not found: {str(e)}"
        except Exception as e:
            return False, None, str(e)
    
    @staticmethod
    @transaction.atomic
    def transfer_between_wallets(from_user, to_user, amount, currency, description):
        """
        Transfer between two wallets atomically.
        Returns: (success: bool, error: str or None)
        """
        success, txn, error = WalletManager.deduct_from_wallet(
            from_user, amount, currency,
            f"Transfer to {to_user.username}",
            transaction_type='transfer'
        )
        
        if not success:
            return False, error
        
        success, _, error = WalletManager.add_to_wallet(
            to_user, amount, currency,
            f"Transfer from {from_user.username}",
            transaction_type='transfer'
        )
        
        if not success:
            # Rollback - would happen automatically due to @transaction.atomic
            return False, error
        
        return True, None


class CurrencyConverter:
    """Convert between EGP, Gold, and Mass"""
    
    @staticmethod
    def get_rates():
        """Get current conversion rates"""
        return GoldMassConversionRate.get_current_rates()
    
    @staticmethod
    def egp_to_gold(egp_amount):
        """Convert EGP to Gold"""
        rates = CurrencyConverter.get_rates()
        return egp_amount * rates.egp_to_gold
    
    @staticmethod
    def egp_to_mass(egp_amount):
        """Convert EGP to Mass"""
        rates = CurrencyConverter.get_rates()
        return egp_amount * rates.egp_to_mass
    
    @staticmethod
    def gold_to_egp(gold_amount):
        """Convert Gold to EGP"""
        rates = CurrencyConverter.get_rates()
        return gold_amount / rates.egp_to_gold
    
    @staticmethod
    def mass_to_egp(mass_amount):
        """Convert Mass to EGP"""
        rates = CurrencyConverter.get_rates()
        return mass_amount / rates.egp_to_mass
    
    @staticmethod
    @transaction.atomic
    def buy_gold(user, amount_egp, gold_to_buy=None):
        """
        Buy Gold using EGP.
        If gold_to_buy is None, auto-calculate from rate.
        """
        if amount_egp <= 0:
            return False, None, "Amount must be positive"
        
        # Deduct EGP
        success, txn, error = WalletManager.deduct_from_wallet(
            user, amount_egp, 'egp',
            f"Purchase {amount_egp} EGP worth of Gold",
            transaction_type='conversion',
            metadata={'conversion_type': 'egp_to_gold'}
        )
        
        if not success:
            return False, None, error
        
        # Calculate Gold amount
        if gold_to_buy is None:
            gold_to_buy = CurrencyConverter.egp_to_gold(amount_egp)
        
        # Add Gold
        success, _, error = WalletManager.add_to_wallet(
            user, gold_to_buy, 'gold',
            f"Received {gold_to_buy:.2f} Gold",
            transaction_type='conversion',
            metadata={'conversion_type': 'egp_to_gold', 'egp_spent': amount_egp}
        )
        
        if not success:
            return False, None, error
        
        return True, gold_to_buy, None
    
    @staticmethod
    @transaction.atomic
    def buy_mass(user, amount_egp, mass_to_buy=None):
        """
        Buy Mass using EGP.
        If mass_to_buy is None, auto-calculate from rate.
        """
        if amount_egp <= 0:
            return False, None, "Amount must be positive"
        
        # Deduct EGP
        success, txn, error = WalletManager.deduct_from_wallet(
            user, amount_egp, 'egp',
            f"Purchase {amount_egp} EGP worth of Mass",
            transaction_type='conversion',
            metadata={'conversion_type': 'egp_to_mass'}
        )
        
        if not success:
            return False, None, error
        
        # Calculate Mass amount
        if mass_to_buy is None:
            mass_to_buy = CurrencyConverter.egp_to_mass(amount_egp)
        
        # Add Mass
        success, _, error = WalletManager.add_to_wallet(
            user, mass_to_buy, 'mass',
            f"Received {mass_to_buy:.2f} Mass",
            transaction_type='conversion',
            metadata={'conversion_type': 'egp_to_mass', 'egp_spent': amount_egp}
        )
        
        if not success:
            return False, None, error
        
        return True, mass_to_buy, None
