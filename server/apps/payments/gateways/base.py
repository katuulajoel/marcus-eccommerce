from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from decimal import Decimal


class PaymentResult:
    """Standardized payment result across all gateways"""

    def __init__(
        self,
        success: bool,
        transaction_id: Optional[str] = None,
        status: str = 'pending',
        message: str = '',
        requires_action: bool = False,
        action_url: Optional[str] = None,
        action_data: Optional[Dict[str, Any]] = None,
        raw_response: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ):
        self.success = success
        self.transaction_id = transaction_id
        self.status = status
        self.message = message
        self.requires_action = requires_action
        self.action_url = action_url
        self.action_data = action_data or {}
        self.raw_response = raw_response or {}
        self.error = error


class AbstractPaymentGateway(ABC):
    """
    Abstract base class for all payment gateways
    Implements the Strategy pattern for payment processing
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize payment gateway with configuration

        Args:
            config: Dictionary containing gateway configuration
                   (api_key, api_secret, environment, etc.)
        """
        self.config = config
        self.environment = config.get('environment', 'sandbox')
        self.is_sandbox = self.environment == 'sandbox'

    @abstractmethod
    def initialize_payment(
        self,
        amount: Decimal,
        currency: str,
        order_id: int,
        customer_data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> PaymentResult:
        """
        Initialize a payment transaction

        Args:
            amount: Payment amount
            currency: Currency code (USD, UGX, etc.)
            order_id: Order ID
            customer_data: Customer information (email, phone, name)
            metadata: Additional metadata

        Returns:
            PaymentResult object
        """
        pass

    @abstractmethod
    def verify_payment(self, transaction_id: str) -> PaymentResult:
        """
        Verify payment status

        Args:
            transaction_id: Gateway-specific transaction ID

        Returns:
            PaymentResult object
        """
        pass

    @abstractmethod
    def process_webhook(self, payload: Dict[str, Any], signature: Optional[str] = None) -> PaymentResult:
        """
        Process webhook from payment gateway

        Args:
            payload: Webhook payload
            signature: Webhook signature for verification

        Returns:
            PaymentResult object
        """
        pass

    def get_supported_currencies(self) -> list[str]:
        """Return list of supported currencies for this gateway"""
        return ['USD']

    def validate_amount(self, amount: Decimal, currency: str) -> bool:
        """Validate if amount is acceptable for the gateway"""
        if amount <= 0:
            return False
        if currency not in self.get_supported_currencies():
            return False
        return True
