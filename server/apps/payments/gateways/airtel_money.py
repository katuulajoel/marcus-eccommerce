import requests
import uuid
import base64
from decimal import Decimal
from typing import Dict, Any, Optional
from .base import AbstractPaymentGateway, PaymentResult


class AirtelMoneyGateway(AbstractPaymentGateway):
    """
    Airtel Money payment gateway implementation

    Uses Airtel Money API
    Documentation: https://developers.airtel.africa/documentation
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client_id = config.get('api_key')
        self.client_secret = config.get('api_secret')
        self.callback_url = config.get('callback_url', '')
        self.country = config.get('country', 'UG')  # Default to Uganda

        # Environment URLs
        if self.is_sandbox:
            self.base_url = 'https://openapiuat.airtel.africa'
        else:
            self.base_url = 'https://openapi.airtel.africa'

    def _get_access_token(self) -> Optional[str]:
        """
        Get OAuth 2.0 access token for API authentication
        """
        url = f'{self.base_url}/auth/oauth2/token'

        headers = {
            'Content-Type': 'application/json',
            'Accept': '*/*'
        }

        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials'
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()

            data = response.json()
            return data.get('access_token')

        except requests.exceptions.RequestException as e:
            print(f'Failed to get Airtel Money access token: {e}')
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
        Initialize Airtel Money payment (Push Payment)

        Requires customer phone number in international format without +
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
                    error='Phone number is required for Airtel Money payments'
                )

            # Clean phone number (remove + and spaces)
            phone = phone.replace('+', '').replace(' ', '').replace('-', '')

            # Get access token
            access_token = self._get_access_token()
            if not access_token:
                return PaymentResult(
                    success=False,
                    status='failed',
                    error='Failed to authenticate with Airtel Money'
                )

            # Generate unique transaction ID
            transaction_id = f'ORDER-{order_id}-{uuid.uuid4().hex[:8].upper()}'

            # Standard Checkout API
            url = f'{self.base_url}/merchant/v1/payments/'

            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
                'X-Country': self.country,
                'X-Currency': currency
            }

            payload = {
                'reference': transaction_id,
                'subscriber': {
                    'country': self.country,
                    'currency': currency,
                    'msisdn': phone
                },
                'transaction': {
                    'amount': float(amount),
                    'country': self.country,
                    'currency': currency,
                    'id': transaction_id
                }
            }

            response = requests.post(url, headers=headers, json=payload)

            if response.status_code in [200, 201]:
                data = response.json()

                # Check if request was successful
                if data.get('status', {}).get('success'):
                    return PaymentResult(
                        success=True,
                        transaction_id=transaction_id,
                        status='processing',
                        message='Payment request sent. Please approve on your phone.',
                        requires_action=True,
                        action_data={
                            'transaction_id': transaction_id,
                            'phone': phone,
                            'instructions': 'Please check your phone for a payment prompt and enter your PIN to complete the transaction.'
                        },
                        raw_response=data
                    )
                else:
                    error_msg = data.get('status', {}).get('message', 'Payment initialization failed')
                    return PaymentResult(
                        success=False,
                        status='failed',
                        error=error_msg,
                        raw_response=data
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
                error=f'Airtel Money payment initialization failed: {str(e)}'
            )

    def verify_payment(self, transaction_id: str) -> PaymentResult:
        """
        Verify Airtel Money payment status

        Query transaction status endpoint
        """
        try:
            access_token = self._get_access_token()
            if not access_token:
                return PaymentResult(
                    success=False,
                    status='failed',
                    error='Failed to authenticate with Airtel Money'
                )

            # Enquiry API
            url = f'{self.base_url}/standard/v1/payments/{transaction_id}'

            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
                'X-Country': self.country
            }

            response = requests.get(url, headers=headers)
            response.raise_for_status()

            data = response.json()

            # Check transaction status
            transaction_status = data.get('data', {}).get('transaction', {}).get('status', '').upper()

            # Map Airtel status to our status
            status_mapping = {
                'TS': 'succeeded',  # Transaction Successful
                'TF': 'failed',      # Transaction Failed
                'TP': 'processing',  # Transaction Pending
                'TA': 'processing',  # Transaction in progress
            }

            status = status_mapping.get(transaction_status, 'pending')
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
        Process Airtel Money callback/webhook

        Airtel sends callbacks to the configured callback URL
        """
        try:
            transaction = payload.get('transaction', {})
            transaction_id = transaction.get('id') or transaction.get('reference')

            if not transaction_id:
                return PaymentResult(
                    success=False,
                    status='failed',
                    error='No transaction ID in webhook payload'
                )

            # Map status from webhook
            transaction_status = transaction.get('status', '').upper()

            status_mapping = {
                'TS': 'succeeded',
                'TF': 'failed',
                'TP': 'processing',
                'TA': 'processing',
            }

            status = status_mapping.get(transaction_status, 'pending')
            success = status == 'succeeded'

            return PaymentResult(
                success=success,
                transaction_id=transaction_id,
                status=status,
                message=f'Payment {status} via webhook',
                raw_response=payload
            )

        except Exception as e:
            return PaymentResult(
                success=False,
                status='failed',
                error=f'Webhook processing error: {str(e)}'
            )

    def get_supported_currencies(self) -> list[str]:
        """Airtel Money supported currencies (depends on country)"""
        return ['UGX', 'KES', 'TZS', 'RWF', 'ZMW', 'MWK', 'NGN', 'XAF', 'XOF', 'MGA', 'SCR']
