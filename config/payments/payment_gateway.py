"""
Mock Payment Gateway for DeepProTeam Marketplace
Provides a pluggable interface for payment processing.
Replace MockPaymentGateway with real providers (Stripe, PayPal) by changing the import.
"""

from decimal import Decimal
from enum import Enum
import uuid
from datetime import datetime


class PaymentStatus(Enum):
    """Payment status enum"""
    PENDING = 'pending'
    COMPLETED = 'completed'
    FAILED = 'failed'
    REFUNDED = 'refunded'


class PaymentResult:
    """Result object for payment operations"""
    
    def __init__(self, success: bool, transaction_id: str = None, 
                 error: str = None, details: dict = None):
        self.success = success
        self.transaction_id = transaction_id or str(uuid.uuid4())
        self.error = error
        self.details = details or {}
        self.timestamp = datetime.utcnow().isoformat()


class BasePaymentGateway:
    """Base class for payment gateway implementations"""
    
    def process_payment(self, amount: Decimal, currency: str, 
                       description: str, metadata: dict = None) -> PaymentResult:
        """
        Process a payment.
        
        Args:
            amount: Payment amount
            currency: Currency code ('egp', 'gold', 'mass')
            description: Payment description
            metadata: Optional metadata (user_id, order_id, etc.)
        
        Returns:
            PaymentResult with success status and transaction ID
        """
        raise NotImplementedError
    
    def refund_payment(self, transaction_id: str, amount: Decimal = None) -> PaymentResult:
        """
        Refund a payment.
        
        Args:
            transaction_id: Original transaction ID
            amount: Partial refund amount (None = full refund)
        
        Returns:
            PaymentResult
        """
        raise NotImplementedError


class MockPaymentGateway(BasePaymentGateway):
    """
    Mock payment gateway for development and testing.
    Simulates successful payments; swap with Stripe/PayPal in production.
    
    To test failures, pass `fail=True` in metadata:
        payment_gateway.process_payment(
            Decimal('100.00'), 
            'egp', 
            'Test', 
            metadata={'fail': True}
        )
    """
    
    def __init__(self):
        self.transactions = {}  # In-memory store for testing
        self.refunds = {}
    
    def process_payment(self, amount: Decimal, currency: str, 
                       description: str, metadata: dict = None) -> PaymentResult:
        """
        Mock payment processing.
        Returns success unless metadata['fail'] = True.
        """
        metadata = metadata or {}
        
        # Simulate failure if requested (for testing error paths)
        if metadata.get('fail'):
            return PaymentResult(
                success=False,
                error=f"Simulated payment failure for {description}",
                details={'currency': currency, 'amount': str(amount)}
            )
        
        # Generate transaction ID
        txn_id = f"mock_{uuid.uuid4().hex[:16]}"
        
        # Store transaction
        self.transactions[txn_id] = {
            'amount': amount,
            'currency': currency,
            'description': description,
            'status': PaymentStatus.COMPLETED.value,
            'timestamp': datetime.utcnow().isoformat(),
            'metadata': metadata
        }
        
        return PaymentResult(
            success=True,
            transaction_id=txn_id,
            details={
                'currency': currency,
                'amount': str(amount),
                'description': description,
                'status': 'completed'
            }
        )
    
    def refund_payment(self, transaction_id: str, amount: Decimal = None) -> PaymentResult:
        """
        Mock refund processing.
        """
        if transaction_id not in self.transactions:
            return PaymentResult(
                success=False,
                error=f"Transaction {transaction_id} not found"
            )
        
        original_txn = self.transactions[transaction_id]
        refund_amount = amount or original_txn['amount']
        
        # Validate partial refund
        if amount and amount > original_txn['amount']:
            return PaymentResult(
                success=False,
                error=f"Refund amount {amount} exceeds original {original_txn['amount']}"
            )
        
        # Create refund record
        refund_id = f"refund_{uuid.uuid4().hex[:16]}"
        self.refunds[refund_id] = {
            'original_txn': transaction_id,
            'refund_amount': refund_amount,
            'status': PaymentStatus.REFUNDED.value,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return PaymentResult(
            success=True,
            transaction_id=refund_id,
            details={
                'original_transaction': transaction_id,
                'refund_amount': str(refund_amount),
                'status': 'refunded'
            }
        )
    
    def get_transaction(self, transaction_id: str) -> dict:
        """Retrieve transaction details (for testing)"""
        return self.transactions.get(transaction_id)


# Production gateway would be imported conditionally:
# from config.payments.stripe_gateway import StripePaymentGateway
# Or from config.payments.paypal_gateway import PayPalPaymentGateway

# For now, default to mock
payment_gateway = MockPaymentGateway()
