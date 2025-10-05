import requests
import uuid
import json
from decimal import Decimal
from typing import Dict, Any, Optional
from .base import AbstractPaymentGateway, PaymentResult


class MTNMoMoGateway(AbstractPaymentGateway):
    """
    MTN Mobile Money payment gateway implementation

    Uses MTN MoMo Collection API
    Documentation: https://momodeveloper.mtn.com/api-documentation/api-description/
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.subscription_key = config.get('api_key')
        self.api_user = config.get('api_user')
        self.api_key = config.get('api_secret')
        self.callback_url = config.get('callback_url', '')

        # Environment URLs
        if self.is_sandbox:
            self.base_url = 'https://sandbox.momodeveloper.mtn.com'
        else:
            self.base_url = 'https://momodeveloper.mtn.com'

    def _get_access_token(self) -> Optional[str]:
        """
        Get OAuth 2.0 access token for API authentication
        """
        url = f'{self.base_url}/collection/token/'

        headers = {
            'Ocp-Apim-Subscription-Key': self.subscription_key,
        }

        try:
            response = requests.post(
                url,
                auth=(self.api_user, self.api_key),
                headers=headers
            )
            response.raise_for_status()

            data = response.json()
            return data.get('access_token')

        except requests.exceptions.RequestException as e:
            print(f'Failed to get MTN MoMo access token: {e}')
            return None

    def initialize_payment(
        self,
        amount: Decimal,
        currency: str,
        order_id: int,
        customer_data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> PaymentResult:
        """
        Initialize MTN MoMo payment (Request to Pay)

        Requires customer phone number in international format (e.g., 256XXXXXXXXX)
        """
        try:
            if not self.validate_amount(amount, currency):
                return PaymentResult(
                    success=False,
                    status='failed',
                    error=f'Invalid amount or currency: {amount} {currency}'
                )

            phone = customer_data.get('phone')
            if not phone:
                return PaymentResult(
                    success=False,
                    status='failed',
                    error='Phone number is required for MTN MoMo payments'
                )

            # Clean phone number (remove + and spaces)
            phone = phone.replace('+', '').replace(' ', '').replace('-', '')

            # Get access token
            access_token = self._get_access_token()
            if not access_token:
                return PaymentResult(
                    success=False,
                    status='failed',
                    error='Failed to authenticate with MTN MoMo'
                )

            # Generate unique reference ID
            reference_id = str(uuid.uuid4())

            # Request to Pay API
            url = f'{self.base_url}/collection/v1_0/requesttopay'

            headers = {
                'Authorization': f'Bearer {access_token}',
                'X-Reference-Id': reference_id,
                'X-Target-Environment': 'sandbox' if self.is_sandbox else 'production',
                'Ocp-Apim-Subscription-Key': self.subscription_key,
                'Content-Type': 'application/json',
            }

            # Add callback URL if configured
            if self.callback_url:
                headers['X-Callback-Url'] = self.callback_url

            payload = {
                'amount': str(amount),
                'currency': currency,
                'externalId': str(order_id),
                'payer': {
                    'partyIdType': 'MSISDN',
                    'partyId': phone
                },
                'payerMessage': f'Payment for order #{order_id}',
                'payeeNote': f'Marcus Custom Cycles - Order #{order_id}'
            }

            response = requests.post(url, headers=headers, json=payload)

            if response.status_code == 202:  # Accepted
                return PaymentResult(
                    success=True,
                    transaction_id=reference_id,
                    status='processing',
                    message='Payment request sent. Please approve on your phone.',
                    requires_action=True,
                    action_data={
                        'reference_id': reference_id,
                        'phone': phone,
                        'instructions': 'Please check your phone for a payment prompt and enter your PIN to complete the transaction.'
                    },
                    raw_response={'reference_id': reference_id, 'status_code': 202}
                )
            else:
                error_data = response.json() if response.content else {}
                return PaymentResult(
                    success=False,
                    status='failed',
                    error=error_data.get('message', f'Request failed with status {response.status_code}'),
                    raw_response=error_data
                )

        except Exception as e:
            return PaymentResult(
                success=False,
                status='failed',
                error=f'MTN MoMo payment initialization failed: {str(e)}'
            )

    def verify_payment(self, transaction_id: str) -> PaymentResult:
        """
        Verify MTN MoMo payment status

        Poll the requesttopay endpoint to check payment status
        """
        try:
            access_token = self._get_access_token()
            if not access_token:
                return PaymentResult(
                    success=False,
                    status='failed',
                    error='Failed to authenticate with MTN MoMo'
                )

            url = f'{self.base_url}/collection/v1_0/requesttopay/{transaction_id}'

            headers = {
                'Authorization': f'Bearer {access_token}',
                'X-Target-Environment': 'sandbox' if self.is_sandbox else 'production',
                'Ocp-Apim-Subscription-Key': self.subscription_key,
            }

            response = requests.get(url, headers=headers)
            response.raise_for_status()

            data = response.json()
            momo_status = data.get('status', '').upper()

            # Map MTN MoMo status to our status
            status_mapping = {
                'SUCCESSFUL': 'succeeded',
                'PENDING': 'processing',
                'FAILED': 'failed',
                'TIMEOUT': 'failed',
            }

            status = status_mapping.get(momo_status, 'pending')
            success = status == 'succeeded'

            return PaymentResult(
                success=success,
                transaction_id=transaction_id,
                status=status,
                message=f'Payment {status}',
                raw_response=data
            )

        except requests.exceptions.RequestException as e:
            return PaymentResult(
                success=False,
                status='failed',
                error=f'Failed to verify payment: {str(e)}'
            )

    def process_webhook(self, payload: Dict[str, Any], signature: Optional[str] = None) -> PaymentResult:
        """
        Process MTN MoMo callback/webhook

        MTN MoMo sends callbacks when payment status changes
        """
        try:
            reference_id = payload.get('referenceId') or payload.get('X-Reference-Id')

            if not reference_id:
                return PaymentResult(
                    success=False,
                    status='failed',
                    error='No reference ID in webhook payload'
                )

            # Verify the payment status
            return self.verify_payment(reference_id)

        except Exception as e:
            return PaymentResult(
                success=False,
                status='failed',
                error=f'Webhook processing error: {str(e)}'
            )

    def get_supported_currencies(self) -> list[str]:
        """MTN MoMo supported currencies (depends on country)"""
        return ['UGX', 'EUR']  # Uganda Shillings (most common), Euro (for sandbox)
