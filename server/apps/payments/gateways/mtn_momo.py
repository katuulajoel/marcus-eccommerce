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

    Configuration (from PaymentGatewayConfig):
        api_secret: Subscription key (Ocp-Apim-Subscription-Key) [required]
        environment: 'sandbox' or 'production' [default: 'sandbox']
        additional_config: {
            api_user: Pre-configured API User UUID [optional, will create if not provided]
            api_key: Pre-configured API Key [optional, will create if not provided]
            callback_url: Webhook callback URL [optional]
        }

    Note: For production, it's recommended to pre-create the API user/key and store them
    in additional_config rather than creating them dynamically.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        print(f"\n=== MTN MoMo Gateway Init ===")
        print(f"Config keys: {list(config.keys())}")
        self.subscription_key = config.get('api_secret')  # This is the Ocp-Apim-Subscription-Key
        self.callback_url = config.get('callback_url', '')

        # Check if API user and key are provided (recommended for production)
        # or if we should create them dynamically (for testing)
        self.api_user = config.get('api_user')  # Pre-configured API User ID
        self.api_key = config.get('api_key')  # Pre-configured API Key

        print(f"API User from config: {self.api_user[:20] if self.api_user else 'None'}...")
        print(f"API Key from config: {self.api_key[:20] if self.api_key else 'None'}...")
        print(f"Subscription Key: {self.subscription_key[:20] if self.subscription_key else 'None'}...")

        # Environment URLs
        if self.is_sandbox:
            self.base_url = 'https://sandbox.momodeveloper.mtn.com'
        else:
            self.base_url = 'https://momoapi.mtn.com'

        # If no API user/key provided, create them dynamically (may have limited permissions)
        if not self.api_user or not self.api_key:
            print("API User or Key missing, initializing credentials...")
            self._initialize_api_credentials()
        print(f"=== End Gateway Init ===\n")

    def _initialize_api_credentials(self) -> None:
        """
        Create API user and API key from subscription key
        This needs to be done once to get credentials for authentication
        """
        try:
            # Step 1: Create API User
            api_user_id = str(uuid.uuid4())
            create_user_url = f'{self.base_url}/v1_0/apiuser'

            headers = {
                'X-Reference-Id': api_user_id,
                'Ocp-Apim-Subscription-Key': self.subscription_key,
                'Content-Type': 'application/json'
            }

            payload = {
                'providerCallbackHost': self.callback_url or 'webhook.site'
            }

            response = requests.post(create_user_url, headers=headers, json=payload)

            if response.status_code == 201:
                self.api_user = api_user_id

                # Step 2: Generate API Key
                create_key_url = f'{self.base_url}/v1_0/apiuser/{api_user_id}/apikey'
                key_headers = {
                    'Ocp-Apim-Subscription-Key': self.subscription_key
                }

                key_response = requests.post(create_key_url, headers=key_headers)

                if key_response.status_code == 201:
                    self.api_key = key_response.json().get('apiKey')
                else:
                    print(f'Failed to create API key: {key_response.status_code}')
            else:
                print(f'Failed to create API user: {response.status_code}')

        except Exception as e:
            print(f'Failed to initialize MTN MoMo credentials: {e}')

    def _get_access_token(self) -> Optional[str]:
        """
        Get OAuth 2.0 access token for API authentication
        Uses Basic Auth with API User (username) and API Key (password)
        """
        url = f'{self.base_url}/collection/token/'

        headers = {
            'Ocp-Apim-Subscription-Key': self.subscription_key,
            'X-Target-Environment': 'sandbox' if self.is_sandbox else 'production',
        }

        try:
            print(f"Getting access token with API User: {self.api_user[:8]}...")
            print(f"API Key: {self.api_key[:20] if self.api_key else 'None'}...")
            response = requests.post(
                url,
                auth=(self.api_user, self.api_key),
                headers=headers
            )
            print(f"Token request status: {response.status_code}")
            response.raise_for_status()

            data = response.json()
            token = data.get('access_token')
            print(f"Access token obtained: {token[:40] if token else 'None'}...")
            print(f"Access token type: {data.get('token_type')}")
            print(f"Access token expires in: {data.get('expires_in')}")
            return token

        except requests.exceptions.RequestException as e:
            print(f'Failed to get MTN MoMo access token: {e}')
            if hasattr(e, 'response') and e.response is not None:
                print(f'Response status: {e.response.status_code}')
                print(f'Response body: {e.response.text}')
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

            # Clean phone number (remove all non-digit characters)
            phone = ''.join(filter(str.isdigit, phone))
            
            # Validate phone number format (should start with country code and be at least 10 digits)
            if not phone.isdigit() or len(phone) < 10:
                return PaymentResult(
                    success=False,
                    status='failed',
                    error='Invalid phone number format. Please use a valid phone number.'
                )

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

            # Generate unique external ID (must be unique per transaction)
            # Use UUID without hyphens to ensure global uniqueness
            external_id = str(uuid.uuid4()).replace('-', '')[:32]  # MTN MoMo max 256 chars

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
            # NOTE: The callback URL host must match the providerCallbackHost
            # configured when the API user was created. If they don't match,
            # omit the X-Callback-Url header entirely.
            if self.callback_url:
                headers['X-Callback-Url'] = self.callback_url

            # Use custom messages from metadata if provided, otherwise use defaults
            # Note: MTN MoMo API doesn't accept # symbol in messages
            payer_message = metadata.get('payerMessage', f'Payment for order {order_id}') if metadata else f'Payment for order {order_id}'
            payee_note = metadata.get('payeeNote', f'Marcus Custom Cycles - Order {order_id}') if metadata else f'Marcus Custom Cycles - Order {order_id}'

            payload = {
                'amount': str(amount),
                'currency': currency,
                'externalId': external_id,  # Use unique external ID
                'payer': {
                    'partyIdType': 'MSISDN',
                    'partyId': phone
                },
                'payerMessage': payer_message,
                'payeeNote': payee_note
            }

            response = requests.post(url, headers=headers, json=payload)

            # Enhanced logging for debugging
            print(f"\n=== MTN MoMo Payment Request ===")
            print(f"URL: {url}")
            print(f"Headers (with auth): {json.dumps({k: ('Bearer ***' if k == 'Authorization' else v) for k, v in headers.items()}, indent=2)}")
            print(f"Access Token (first 20 chars): {access_token[:20] if access_token else 'None'}...")
            print(f"Payload: {json.dumps(payload, indent=2)}")
            print(f"Response Status: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            print(f"Response Body: {response.text}")
            if response.status_code == 400:
                print(f"ERROR: MTN MoMo returned 400 Bad Request")
                print(f"Common causes:")
                print(f"  1. Phone number not registered in sandbox")
                print(f"  2. Invalid phone number format (should be international format like 256XXXXXXXXX)")
                print(f"  3. Currency not supported (EUR or UGX only)")
                print(f"  4. Invalid API credentials or expired access token")
            print(f"=== End MTN MoMo Request ===\n")

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

                # Provide user-friendly error message for 400 errors
                if response.status_code == 400:
                    error_msg = 'Payment request failed. Please ensure your MTN Mobile Money account is active and the phone number is correct.'
                else:
                    error_msg = error_data.get('message', f'Request failed with status {response.status_code}')

                return PaymentResult(
                    success=False,
                    status='failed',
                    error=error_msg,
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
