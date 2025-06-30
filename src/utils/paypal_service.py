import requests
import json
import base64
from flask import current_app
from datetime import datetime, timezone

class PayPalService:
    """PayPal API integration service for handling payments."""
    
    def __init__(self):
        self.client_id = current_app.config.get('PAYPAL_CLIENT_ID')
        self.client_secret = current_app.config.get('PAYPAL_CLIENT_SECRET')
        self.sandbox_mode = current_app.config.get('PAYPAL_SANDBOX_MODE', True)
        
        # PayPal API URLs
        if self.sandbox_mode:
            self.base_url = 'https://api-m.sandbox.paypal.com'
            self.web_url = 'https://www.sandbox.paypal.com'
        else:
            self.base_url = 'https://api-m.paypal.com'
            self.web_url = 'https://www.paypal.com'
    
    def get_access_token(self):
        """Get OAuth access token from PayPal."""
        if not self.client_id or not self.client_secret:
            raise ValueError("PayPal credentials not configured")
        
        url = f"{self.base_url}/v1/oauth2/token"
        
        # Encode credentials
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            'Accept': 'application/json',
            'Accept-Language': 'en_US',
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = 'grant_type=client_credentials'
        
        try:
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            return token_data['access_token']
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to get PayPal access token: {str(e)}")
    
    def create_order(self, amount, currency='USD', return_url=None, cancel_url=None):
        """Create a PayPal order for payment."""
        access_token = self.get_access_token()
        
        url = f"{self.base_url}/v2/checkout/orders"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}',
            'PayPal-Request-Id': f'order-{datetime.now(timezone.utc).timestamp()}'
        }
        
        # Default URLs if not provided
        if not return_url:
            return_url = current_app.config.get('PAYPAL_RETURN_URL', 'http://localhost:3000/payment/success')
        if not cancel_url:
            cancel_url = current_app.config.get('PAYPAL_CANCEL_URL', 'http://localhost:3000/payment/cancel')
        
        order_data = {
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "amount": {
                        "currency_code": currency,
                        "value": str(amount)
                    },
                    "description": "Cognitive Persuasion Engine Credits"
                }
            ],
            "payment_source": {
                "paypal": {
                    "experience_context": {
                        "payment_method_preference": "IMMEDIATE_PAYMENT_REQUIRED",
                        "brand_name": "Cognitive Persuasion Engine",
                        "locale": "en-US",
                        "landing_page": "LOGIN",
                        "shipping_preference": "NO_SHIPPING",
                        "user_action": "PAY_NOW",
                        "return_url": return_url,
                        "cancel_url": cancel_url
                    }
                }
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=order_data)
            response.raise_for_status()
            
            order = response.json()
            
            # Extract approval URL
            approval_url = None
            for link in order.get('links', []):
                if link.get('rel') == 'payer-action':
                    approval_url = link.get('href')
                    break
            
            return {
                'order_id': order['id'],
                'status': order['status'],
                'approval_url': approval_url,
                'order_data': order
            }
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to create PayPal order: {str(e)}")
    
    def capture_order(self, order_id):
        """Capture payment for an approved PayPal order."""
        access_token = self.get_access_token()
        
        url = f"{self.base_url}/v2/checkout/orders/{order_id}/capture"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}',
            'PayPal-Request-Id': f'capture-{datetime.now(timezone.utc).timestamp()}'
        }
        
        try:
            response = requests.post(url, headers=headers)
            response.raise_for_status()
            
            capture_data = response.json()
            
            # Check if capture was successful
            if capture_data.get('status') == 'COMPLETED':
                purchase_units = capture_data.get('purchase_units', [])
                if purchase_units:
                    captures = purchase_units[0].get('payments', {}).get('captures', [])
                    if captures:
                        capture = captures[0]
                        return {
                            'success': True,
                            'capture_id': capture.get('id'),
                            'amount': capture.get('amount', {}).get('value'),
                            'currency': capture.get('amount', {}).get('currency_code'),
                            'status': capture.get('status'),
                            'create_time': capture.get('create_time'),
                            'capture_data': capture_data
                        }
            
            return {
                'success': False,
                'status': capture_data.get('status'),
                'capture_data': capture_data
            }
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to capture PayPal order: {str(e)}")
    
    def get_order_details(self, order_id):
        """Get details of a PayPal order."""
        access_token = self.get_access_token()
        
        url = f"{self.base_url}/v2/checkout/orders/{order_id}"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to get PayPal order details: {str(e)}")
    
    def verify_webhook_signature(self, headers, body, webhook_id):
        """Verify PayPal webhook signature for security."""
        access_token = self.get_access_token()
        
        url = f"{self.base_url}/v1/notifications/verify-webhook-signature"
        
        auth_headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
        
        verification_data = {
            'auth_algo': headers.get('PAYPAL-AUTH-ALGO'),
            'cert_id': headers.get('PAYPAL-CERT-ID'),
            'transmission_id': headers.get('PAYPAL-TRANSMISSION-ID'),
            'transmission_sig': headers.get('PAYPAL-TRANSMISSION-SIG'),
            'transmission_time': headers.get('PAYPAL-TRANSMISSION-TIME'),
            'webhook_id': webhook_id,
            'webhook_event': json.loads(body) if isinstance(body, str) else body
        }
        
        try:
            response = requests.post(url, headers=auth_headers, json=verification_data)
            response.raise_for_status()
            
            result = response.json()
            return result.get('verification_status') == 'SUCCESS'
            
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Failed to verify PayPal webhook: {str(e)}")
            return False
    
    def is_configured(self):
        """Check if PayPal service is properly configured."""
        return bool(self.client_id and self.client_secret)
    
    def get_configuration_status(self):
        """Get configuration status for debugging."""
        return {
            'client_id_configured': bool(self.client_id),
            'client_secret_configured': bool(self.client_secret),
            'sandbox_mode': self.sandbox_mode,
            'base_url': self.base_url
        }

