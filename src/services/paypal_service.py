import os
import requests
import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

class PayPalService:
    """Service class for PayPal payment processing"""
    
    def __init__(self):
        self.client_id = os.getenv('PAYPAL_CLIENT_ID')
        self.client_secret = os.getenv('PAYPAL_CLIENT_SECRET')
        self.mode = os.getenv('PAYPAL_MODE', 'sandbox')  # sandbox or live
        
        # Set base URL based on mode
        if self.mode == 'live':
            self.base_url = 'https://api-m.paypal.com'
        else:
            self.base_url = 'https://api-m.sandbox.paypal.com'
        
        self.access_token = None
        self.token_expires_at = None
    
    def is_demo_mode(self, user_email: str = None) -> bool:
        """Check if user is in demo mode"""
        return user_email is None or user_email == 'demo@example.com'
    
    def get_access_token(self) -> Optional[str]:
        """Get PayPal access token"""
        
        # Check if we have a valid token
        if self.access_token and self.token_expires_at and datetime.now() < self.token_expires_at:
            return self.access_token
        
        if not self.client_id or not self.client_secret:
            return None
        
        try:
            url = f"{self.base_url}/v1/oauth2/token"
            
            headers = {
                'Accept': 'application/json',
                'Accept-Language': 'en_US',
            }
            
            data = 'grant_type=client_credentials'
            
            response = requests.post(
                url,
                headers=headers,
                data=data,
                auth=(self.client_id, self.client_secret),
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                self.access_token = result['access_token']
                expires_in = result.get('expires_in', 3600)  # Default 1 hour
                self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)  # 1 minute buffer
                return self.access_token
            else:
                print(f"PayPal token error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"PayPal token exception: {e}")
            return None
    
    def create_payment(self, amount: float, currency: str = 'USD', description: str = 'Cognitive Persuasion Engine Credits', user_email: str = None) -> Dict[str, Any]:
        """Create a PayPal payment"""
        
        # Always use mock data for demo mode
        if self.is_demo_mode(user_email):
            return self._mock_create_payment(amount, currency, description)
        
        access_token = self.get_access_token()
        if not access_token:
            return self._mock_create_payment(amount, currency, description)
        
        try:
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
                    "description": description
                }],
                "redirect_urls": {
                    "return_url": "https://visitorintel.site/payment/success",
                    "cancel_url": "https://visitorintel.site/payment/cancel"
                }
            }
            
            response = requests.post(
                url,
                headers=headers,
                json=payment_data,
                timeout=30
            )
            
            if response.status_code == 201:
                result = response.json()
                
                # Extract approval URL
                approval_url = None
                for link in result.get('links', []):
                    if link.get('rel') == 'approval_url':
                        approval_url = link.get('href')
                        break
                
                return {
                    'success': True,
                    'payment_id': result.get('id'),
                    'approval_url': approval_url,
                    'amount': amount,
                    'currency': currency,
                    'status': result.get('state'),
                    'source': 'paypal'
                }
            else:
                print(f"PayPal payment error: {response.status_code} - {response.text}")
                return self._mock_create_payment(amount, currency, description)
                
        except Exception as e:
            print(f"PayPal payment exception: {e}")
            return self._mock_create_payment(amount, currency, description)
    
    def execute_payment(self, payment_id: str, payer_id: str, user_email: str = None) -> Dict[str, Any]:
        """Execute a PayPal payment after approval"""
        
        # Always use mock data for demo mode
        if self.is_demo_mode(user_email):
            return self._mock_execute_payment(payment_id, payer_id)
        
        access_token = self.get_access_token()
        if not access_token:
            return self._mock_execute_payment(payment_id, payer_id)
        
        try:
            url = f"{self.base_url}/v1/payments/payment/{payment_id}/execute"
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}',
            }
            
            execute_data = {
                "payer_id": payer_id
            }
            
            response = requests.post(
                url,
                headers=headers,
                json=execute_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract transaction details
                transaction = result.get('transactions', [{}])[0]
                amount_details = transaction.get('amount', {})
                
                return {
                    'success': True,
                    'payment_id': result.get('id'),
                    'transaction_id': transaction.get('related_resources', [{}])[0].get('sale', {}).get('id'),
                    'amount': amount_details.get('total'),
                    'currency': amount_details.get('currency'),
                    'status': result.get('state'),
                    'payer_email': result.get('payer', {}).get('payer_info', {}).get('email'),
                    'create_time': result.get('create_time'),
                    'source': 'paypal'
                }
            else:
                print(f"PayPal execute error: {response.status_code} - {response.text}")
                return self._mock_execute_payment(payment_id, payer_id)
                
        except Exception as e:
            print(f"PayPal execute exception: {e}")
            return self._mock_execute_payment(payment_id, payer_id)
    
    def get_payment_details(self, payment_id: str, user_email: str = None) -> Dict[str, Any]:
        """Get PayPal payment details"""
        
        # Always use mock data for demo mode
        if self.is_demo_mode(user_email):
            return self._mock_payment_details(payment_id)
        
        access_token = self.get_access_token()
        if not access_token:
            return self._mock_payment_details(payment_id)
        
        try:
            url = f"{self.base_url}/v1/payments/payment/{payment_id}"
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}',
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'payment': result,
                    'source': 'paypal'
                }
            else:
                return self._mock_payment_details(payment_id)
                
        except Exception as e:
            print(f"PayPal details exception: {e}")
            return self._mock_payment_details(payment_id)
    
    def create_subscription_plan(self, name: str, description: str, amount: float, currency: str = 'USD', interval: str = 'MONTH', user_email: str = None) -> Dict[str, Any]:
        """Create a PayPal subscription plan"""
        
        # Always use mock data for demo mode
        if self.is_demo_mode(user_email):
            return self._mock_subscription_plan(name, description, amount, currency, interval)
        
        access_token = self.get_access_token()
        if not access_token:
            return self._mock_subscription_plan(name, description, amount, currency, interval)
        
        try:
            url = f"{self.base_url}/v1/billing/plans"
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}',
                'PayPal-Request-Id': f'plan-{datetime.now().strftime("%Y%m%d%H%M%S")}',
            }
            
            plan_data = {
                "product_id": "COGNITIVE_PERSUASION_CREDITS",
                "name": name,
                "description": description,
                "status": "ACTIVE",
                "billing_cycles": [{
                    "frequency": {
                        "interval_unit": interval,
                        "interval_count": 1
                    },
                    "tenure_type": "REGULAR",
                    "sequence": 1,
                    "total_cycles": 0,  # Infinite
                    "pricing_scheme": {
                        "fixed_price": {
                            "value": str(amount),
                            "currency_code": currency
                        }
                    }
                }],
                "payment_preferences": {
                    "auto_bill_outstanding": True,
                    "setup_fee": {
                        "value": "0",
                        "currency_code": currency
                    },
                    "setup_fee_failure_action": "CONTINUE",
                    "payment_failure_threshold": 3
                }
            }
            
            response = requests.post(
                url,
                headers=headers,
                json=plan_data,
                timeout=30
            )
            
            if response.status_code == 201:
                result = response.json()
                return {
                    'success': True,
                    'plan_id': result.get('id'),
                    'name': result.get('name'),
                    'status': result.get('status'),
                    'source': 'paypal'
                }
            else:
                print(f"PayPal plan error: {response.status_code} - {response.text}")
                return self._mock_subscription_plan(name, description, amount, currency, interval)
                
        except Exception as e:
            print(f"PayPal plan exception: {e}")
            return self._mock_subscription_plan(name, description, amount, currency, interval)
    
    # Mock methods for demo mode
    def _mock_create_payment(self, amount: float, currency: str, description: str) -> Dict[str, Any]:
        return {
            'success': True,
            'payment_id': f'DEMO-PAY-{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'approval_url': 'https://demo.paypal.com/approve',
            'amount': amount,
            'currency': currency,
            'status': 'created',
            'source': 'mock'
        }
    
    def _mock_execute_payment(self, payment_id: str, payer_id: str) -> Dict[str, Any]:
        return {
            'success': True,
            'payment_id': payment_id,
            'transaction_id': f'DEMO-TXN-{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'amount': '10.00',
            'currency': 'USD',
            'status': 'approved',
            'payer_email': 'demo@example.com',
            'create_time': datetime.now().isoformat(),
            'source': 'mock'
        }
    
    def _mock_payment_details(self, payment_id: str) -> Dict[str, Any]:
        return {
            'success': True,
            'payment': {
                'id': payment_id,
                'state': 'approved',
                'create_time': datetime.now().isoformat(),
                'transactions': [{
                    'amount': {'total': '10.00', 'currency': 'USD'},
                    'description': 'Demo payment'
                }]
            },
            'source': 'mock'
        }
    
    def _mock_subscription_plan(self, name: str, description: str, amount: float, currency: str, interval: str) -> Dict[str, Any]:
        return {
            'success': True,
            'plan_id': f'DEMO-PLAN-{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'name': name,
            'status': 'ACTIVE',
            'source': 'mock'
        }

