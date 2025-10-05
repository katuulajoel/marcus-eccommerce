import stripe
from decimal import Decimal
from typing import Dict, Any, Optional
from .base import AbstractPaymentGateway, PaymentResult


class StripeGateway(AbstractPaymentGateway):
    """Stripe payment gateway implementation"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        stripe.api_key = config.get('api_secret')
        self.webhook_secret = config.get('webhook_secret', '')

    def initialize_payment(
        self,
        amount: Decimal,
        currency: str,
        order_id: int,
        customer_data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> PaymentResult:
        """
        Initialize a Stripe Payment Intent

        Creates a PaymentIntent and returns client_secret for frontend
        """
        try:
            if not self.validate_amount(amount, currency):
                return PaymentResult(
                    success=False,
                    status='failed',
                    error=f'Invalid amount or currency: {amount} {currency}'
                )

            # Stripe amounts are in cents
            stripe_amount = int(amount * 100)

            payment_intent_data = {
                'amount': stripe_amount,
                'currency': currency.lower(),
                'metadata': {
                    'order_id': str(order_id),
                    **(metadata or {})
                },
                'receipt_email': customer_data.get('email'),
            }

            # Add customer if email exists
            if customer_data.get('email'):
                # Try to find or create customer
                customers = stripe.Customer.list(email=customer_data['email'], limit=1)
                if customers.data:
                    payment_intent_data['customer'] = customers.data[0].id
                else:
                    customer = stripe.Customer.create(
                        email=customer_data['email'],
                        name=customer_data.get('name'),
                        phone=customer_data.get('phone')
                    )
                    payment_intent_data['customer'] = customer.id

            # Create payment intent
            intent = stripe.PaymentIntent.create(**payment_intent_data)

            return PaymentResult(
                success=True,
                transaction_id=intent.id,
                status='pending',
                message='Payment initiated successfully',
                requires_action=True,
                action_data={
                    'client_secret': intent.client_secret,
                    'publishable_key': self.config.get('api_key')
                },
                raw_response=intent.to_dict()
            )

        except stripe.StripeError as e:
            return PaymentResult(
                success=False,
                status='failed',
                error=str(e),
                message='Failed to initialize payment'
            )

    def verify_payment(self, transaction_id: str) -> PaymentResult:
        """
        Verify Stripe Payment Intent status
        """
        try:
            intent = stripe.PaymentIntent.retrieve(transaction_id)

            status_mapping = {
                'succeeded': 'succeeded',
                'processing': 'processing',
                'requires_payment_method': 'pending',
                'requires_confirmation': 'pending',
                'requires_action': 'requires_action',
                'canceled': 'cancelled',
                'requires_capture': 'pending',
            }

            status = status_mapping.get(intent.status, 'pending')
            success = status == 'succeeded'

            return PaymentResult(
                success=success,
                transaction_id=intent.id,
                status=status,
                message=f'Payment {status}',
                raw_response=intent.to_dict()
            )

        except stripe.StripeError as e:
            return PaymentResult(
                success=False,
                status='failed',
                error=str(e),
                message='Failed to verify payment'
            )

    def process_webhook(self, payload: Dict[str, Any], signature: Optional[str] = None) -> PaymentResult:
        """
        Process Stripe webhook event
        """
        try:
            # Verify webhook signature
            if self.webhook_secret and signature:
                event = stripe.Webhook.construct_event(
                    payload, signature, self.webhook_secret
                )
            else:
                event = stripe.Event.construct_from(payload, stripe.api_key)

            # Handle payment intent events
            if event.type == 'payment_intent.succeeded':
                payment_intent = event.data.object

                return PaymentResult(
                    success=True,
                    transaction_id=payment_intent.id,
                    status='succeeded',
                    message='Payment succeeded',
                    raw_response=payment_intent
                )

            elif event.type == 'payment_intent.payment_failed':
                payment_intent = event.data.object

                return PaymentResult(
                    success=False,
                    transaction_id=payment_intent.id,
                    status='failed',
                    error=payment_intent.get('last_payment_error', {}).get('message', 'Payment failed'),
                    raw_response=payment_intent
                )

            elif event.type == 'payment_intent.canceled':
                payment_intent = event.data.object

                return PaymentResult(
                    success=False,
                    transaction_id=payment_intent.id,
                    status='cancelled',
                    message='Payment cancelled',
                    raw_response=payment_intent
                )

            # Unknown event type
            return PaymentResult(
                success=False,
                status='pending',
                message=f'Unhandled event type: {event.type}'
            )

        except stripe.SignatureVerificationError as e:
            return PaymentResult(
                success=False,
                status='failed',
                error=f'Invalid webhook signature: {str(e)}'
            )
        except Exception as e:
            return PaymentResult(
                success=False,
                status='failed',
                error=f'Webhook processing error: {str(e)}'
            )

    def get_supported_currencies(self) -> list[str]:
        """Stripe supports many currencies"""
        return ['USD', 'EUR', 'GBP', 'UGX', 'KES', 'TZS', 'NGN', 'ZAR']
