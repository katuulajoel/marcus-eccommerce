from typing import Optional, Dict, Any
from decimal import Decimal
from django.utils import timezone

from .models import PaymentGatewayConfig, PaymentTransaction
from .gateways.base import AbstractPaymentGateway, PaymentResult
from .gateways.stripe import StripeGateway
from .gateways.mtn_momo import MTNMoMoGateway
from .gateways.airtel_money import AirtelMoneyGateway
from apps.orders.models import Orders, Payment


class PaymentService:
    """
    Payment service using Factory pattern
    Handles gateway selection and payment processing
    """

    # Gateway registry
    GATEWAYS = {
        'stripe': StripeGateway,
        'mtn_momo': MTNMoMoGateway,
        'airtel_money': AirtelMoneyGateway,
    }

    @classmethod
    def get_gateway(cls, gateway_name: str) -> Optional[AbstractPaymentGateway]:
        """
        Factory method to create gateway instance

        Args:
            gateway_name: Name of the payment gateway (stripe, mtn_momo, airtel_money)

        Returns:
            Payment gateway instance or None
        """
        try:
            # Get gateway configuration
            config = PaymentGatewayConfig.objects.get(
                gateway_name=gateway_name,
                is_active=True
            )

            # Get gateway class
            gateway_class = cls.GATEWAYS.get(gateway_name)
            if not gateway_class:
                raise ValueError(f'Unknown gateway: {gateway_name}')

            # Create gateway instance with configuration
            gateway_config = {
                'api_key': config.api_key,
                'api_secret': config.api_secret,
                'environment': config.environment,
                'webhook_secret': config.webhook_secret,
                **config.additional_config
            }

            return gateway_class(gateway_config)

        except PaymentGatewayConfig.DoesNotExist:
            print(f'Gateway configuration not found or inactive: {gateway_name}')
            return None

    @classmethod
    def initiate_payment(
        cls,
        order_id: int,
        gateway_name: str,
        amount: Decimal,
        currency: str = 'USD',
        customer_data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> tuple[PaymentTransaction, PaymentResult]:
        """
        Initiate a payment transaction

        Args:
            order_id: Order ID
            gateway_name: Payment gateway to use
            amount: Payment amount
            currency: Currency code
            customer_data: Customer information
            metadata: Additional metadata

        Returns:
            Tuple of (PaymentTransaction instance, PaymentResult from gateway)
        """
        try:
            # Get order
            order = Orders.objects.get(id=order_id)

            # Get gateway
            gateway = cls.get_gateway(gateway_name)
            if not gateway:
                raise ValueError(f'Gateway not available: {gateway_name}')

            # Prepare customer data
            if not customer_data:
                customer_data = {
                    'email': order.customer.email,
                    'phone': order.customer.phone,
                    'name': order.customer.name
                }

            # Initialize payment with gateway
            result = gateway.initialize_payment(
                amount=amount,
                currency=currency,
                order_id=order_id,
                customer_data=customer_data,
                metadata=metadata
            )

            # Create transaction record
            transaction = PaymentTransaction.objects.create(
                order=order,
                gateway=gateway_name,
                amount=amount,
                currency=currency,
                status=result.status,
                gateway_transaction_id=result.transaction_id,
                customer_phone=customer_data.get('phone'),
                customer_email=customer_data.get('email'),
                gateway_response=result.raw_response,
                error_message=result.error,
                metadata=metadata or {}
            )

            return transaction, result

        except Orders.DoesNotExist:
            raise ValueError(f'Order not found: {order_id}')
        except Exception as e:
            # Create failed transaction record
            transaction = PaymentTransaction.objects.create(
                order_id=order_id,
                gateway=gateway_name,
                amount=amount,
                currency=currency,
                status='failed',
                error_message=str(e)
            )
            raise

    @classmethod
    def verify_payment(cls, transaction_id: int) -> PaymentResult:
        """
        Verify payment status

        Args:
            transaction_id: PaymentTransaction ID

        Returns:
            PaymentResult object
        """
        try:
            transaction = PaymentTransaction.objects.get(id=transaction_id)

            # Get gateway
            gateway = cls.get_gateway(transaction.gateway)
            if not gateway:
                return PaymentResult(
                    success=False,
                    status='failed',
                    error=f'Gateway not available: {transaction.gateway}'
                )

            # Verify with gateway
            result = gateway.verify_payment(transaction.gateway_transaction_id)

            # Update transaction
            transaction.status = result.status
            transaction.gateway_response = result.raw_response
            transaction.error_message = result.error

            if result.success:
                transaction.completed_at = timezone.now()

            transaction.save()

            # Create Payment record if successful and not already created
            if result.success and not hasattr(transaction, 'payment'):
                cls._create_payment_record(transaction)

            return result

        except PaymentTransaction.DoesNotExist:
            return PaymentResult(
                success=False,
                status='failed',
                error=f'Transaction not found: {transaction_id}'
            )

    @classmethod
    def process_webhook(
        cls,
        gateway_name: str,
        payload: Dict[str, Any],
        signature: Optional[str] = None
    ) -> PaymentResult:
        """
        Process payment gateway webhook

        Args:
            gateway_name: Payment gateway name
            payload: Webhook payload
            signature: Webhook signature (for verification)

        Returns:
            PaymentResult object
        """
        try:
            # Get gateway
            gateway = cls.get_gateway(gateway_name)
            if not gateway:
                return PaymentResult(
                    success=False,
                    status='failed',
                    error=f'Gateway not available: {gateway_name}'
                )

            # Process webhook
            result = gateway.process_webhook(payload, signature)

            # Find transaction by gateway transaction ID
            if result.transaction_id:
                try:
                    transaction = PaymentTransaction.objects.get(
                        gateway_transaction_id=result.transaction_id,
                        gateway=gateway_name
                    )

                    # Update transaction
                    transaction.status = result.status
                    transaction.gateway_response = result.raw_response
                    transaction.error_message = result.error

                    if result.success:
                        transaction.completed_at = timezone.now()

                    transaction.save()

                    # Create Payment record if successful
                    if result.success and not hasattr(transaction, 'payment'):
                        cls._create_payment_record(transaction)

                except PaymentTransaction.DoesNotExist:
                    pass  # Transaction not found, webhook might be for unknown transaction

            return result

        except Exception as e:
            return PaymentResult(
                success=False,
                status='failed',
                error=f'Webhook processing error: {str(e)}'
            )

    @classmethod
    def _create_payment_record(cls, transaction: PaymentTransaction):
        """
        Create Payment record from successful transaction

        Args:
            transaction: PaymentTransaction instance
        """
        payment = Payment.objects.create(
            order=transaction.order,
            amount=transaction.amount,
            payment_method=transaction.gateway,
            paid_by='customer',
            transaction_reference=transaction.gateway_transaction_id
        )

        transaction.payment = payment
        transaction.save()

    @classmethod
    def get_available_gateways(cls) -> list:
        """
        Get list of active payment gateways

        Returns:
            List of gateway configurations
        """
        return PaymentGatewayConfig.objects.filter(is_active=True).values(
            'gateway_name', 'environment'
        )
