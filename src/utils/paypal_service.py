import requests
import json
from flask import current_app
from datetime import datetime, timedelta

class PayPalService:
    """Service class for handling PayPal API integration."""
    
    def __init__(self):
        self.client_id = current_app.config.get('PAYPAL_CLIENT_ID')
        self.client_secret = current_app.config.get('PAYPAL_CLIENT_SECRET')
        self.mode = current_app.config.get('PAYPAL_MODE', 'sandbox')
        
        # Set API base URL based on mode
        if self.mode == 'live':
            self.base_url = 'https://api.paypal.com'
        else:
            self.base_url = 'https://api.sandbox.paypal.com'
        
        self.access_token = None
        self.token_expires_at = None
    
    def get_access_token(self):
        """Get or refresh PayPal access token."""
        
        # Check if we have a valid token
        if self.access_token and self.token_expires_at:
            if datetime.now() < self.token_expires_at:
                return self.access_token
        
        # Request new access token
        url = f"{self.base_url}/v1/oauth2/token"
        
        headers = {
            'Accept': 'application/json',
            'Accept-Language': 'en_US',
        }
        
        data = 'grant_type=client_credentials'
        
        try:
            response = requests.post(
                url,
                headers=headers,
                data=data,
                auth=(self.client_id, self.client_secret)
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data['access_token']
                
                # Set expiration time (subtract 5 minutes for safety)
                expires_in = token_data.get('expires_in', 3600)
                self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 300)
                
                return self.access_token
            else:
                print(f"PayPal token request failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error getting PayPal access token: {str(e)}")
            return None
    
    def create_payment(self, amount, currency, description, return_url, cancel_url, custom_data=None):
        """Create a PayPal payment."""
        
        access_token = self.get_access_token()
        if not access_token:
            raise Exception("Failed to get PayPal access token")
        
        url = f"{self.base_url}/v1/payments/payment"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}',
        }
        
        payment_data = {
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "transactions": [{
                "amount": {
                    "total": str(amount),
                    "currency": currency
                },
                "description": description,
                "custom": custom_data or ""
            }],
            "redirect_urls": {
                "return_url": return_url,
                "cancel_url": cancel_url
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=payment_data)
            
            if response.status_code == 201:
                payment_response = response.json()
                
                # Extract approval URL
                approval_url = None
                for link in payment_response.get('links', []):
                    if link.get('rel') == 'approval_url':
                        approval_url = link.get('href')
                        break
                
                return {
                    'payment_id': payment_response['id'],
                    'approval_url': approval_url,
                    'state': payment_response.get('state'),
                    'create_time': payment_response.get('create_time')
                }
            else:
                print(f"PayPal payment creation failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error creating PayPal payment: {str(e)}")
            return None
    
    def execute_payment(self, payment_id, payer_id):
        """Execute a PayPal payment after user approval."""
        
        access_token = self.get_access_token()
        if not access_token:
            raise Exception("Failed to get PayPal access token")
        
        url = f"{self.base_url}/v1/payments/payment/{payment_id}/execute"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}',
        }
        
        execute_data = {
            "payer_id": payer_id
        }
        
        try:
            response = requests.post(url, headers=headers, json=execute_data)
            
            if response.status_code == 200:
                execution_response = response.json()
                
                # Extract fee information if available
                paypal_fee = 0
                transactions = execution_response.get('transactions', [])
                if transactions:
                    related_resources = transactions[0].get('related_resources', [])
                    for resource in related_resources:
                        if 'sale' in resource:
                            transaction_fee = resource['sale'].get('transaction_fee', {})
                            if transaction_fee:
                                paypal_fee = float(transaction_fee.get('value', 0))
                
                return {
                    'payment_id': execution_response['id'],
                    'state': execution_response.get('state'),
                    'create_time': execution_response.get('create_time'),
                    'paypal_fee': paypal_fee,
                    'payment_method': execution_response.get('payer', {}).get('payment_method')
                }
            else:
                print(f"PayPal payment execution failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error executing PayPal payment: {str(e)}")
            return None
    
    def get_payment_details(self, payment_id):
        """Get details of a PayPal payment."""
        
        access_token = self.get_access_token()
        if not access_token:
            raise Exception("Failed to get PayPal access token")
        
        url = f"{self.base_url}/v1/payments/payment/{payment_id}"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}',
        }
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"PayPal payment details request failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error getting PayPal payment details: {str(e)}")
            return None
    
    def refund_payment(self, sale_id, amount=None, currency='USD'):
        """Refund a PayPal payment (full or partial)."""
        
        access_token = self.get_access_token()
        if not access_token:
            raise Exception("Failed to get PayPal access token")
        
        url = f"{self.base_url}/v1/payments/sale/{sale_id}/refund"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}',
        }
        
        refund_data = {}
        if amount:
            refund_data['amount'] = {
                'total': str(amount),
                'currency': currency
            }
        
        try:
            response = requests.post(url, headers=headers, json=refund_data)
            
            if response.status_code == 201:
                return response.json()
            else:
                print(f"PayPal refund failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error processing PayPal refund: {str(e)}")
            return None
    
    def verify_webhook_signature(self, webhook_data, headers):
        """Verify PayPal webhook signature for security."""
        
        # This would implement webhook signature verification
        # For now, we'll return True (implement proper verification in production)
        return True
    
    def is_configured(self):
        """Check if PayPal is properly configured."""
        return bool(self.client_id and self.client_secret)

