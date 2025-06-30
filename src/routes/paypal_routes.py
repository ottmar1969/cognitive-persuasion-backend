from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from src.services.paypal_service import PayPalService

paypal_bp = Blueprint('paypal', __name__)
paypal_service = PayPalService()

@paypal_bp.route('/create-payment', methods=['POST'])
@jwt_required()
def create_payment():
    """Create a PayPal payment"""
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        amount = data.get('amount')
        currency = data.get('currency', 'USD')
        description = data.get('description', 'Cognitive Persuasion Engine Credits')
        
        if not amount or amount <= 0:
            return jsonify({'error': 'Valid amount is required'}), 400
        
        result = paypal_service.create_payment(amount, currency, description, current_user)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': 'Payment created successfully',
            'demo_mode': paypal_service.is_demo_mode(current_user)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@paypal_bp.route('/execute-payment', methods=['POST'])
@jwt_required()
def execute_payment():
    """Execute a PayPal payment after approval"""
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        payment_id = data.get('payment_id')
        payer_id = data.get('payer_id')
        
        if not payment_id or not payer_id:
            return jsonify({'error': 'Payment ID and Payer ID are required'}), 400
        
        result = paypal_service.execute_payment(payment_id, payer_id, current_user)
        
        if result.get('success'):
            # Here you would typically:
            # 1. Update user's credit balance in database
            # 2. Create transaction record
            # 3. Send confirmation email
            pass
        
        return jsonify({
            'success': True,
            'data': result,
            'message': 'Payment executed successfully',
            'demo_mode': paypal_service.is_demo_mode(current_user)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@paypal_bp.route('/payment-details/<payment_id>', methods=['GET'])
@jwt_required()
def get_payment_details(payment_id):
    """Get PayPal payment details"""
    try:
        current_user = get_jwt_identity()
        
        result = paypal_service.get_payment_details(payment_id, current_user)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': 'Payment details retrieved successfully',
            'demo_mode': paypal_service.is_demo_mode(current_user)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@paypal_bp.route('/create-subscription-plan', methods=['POST'])
@jwt_required()
def create_subscription_plan():
    """Create a PayPal subscription plan"""
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        name = data.get('name')
        description = data.get('description')
        amount = data.get('amount')
        currency = data.get('currency', 'USD')
        interval = data.get('interval', 'MONTH')
        
        if not name or not description or not amount:
            return jsonify({'error': 'Name, description, and amount are required'}), 400
        
        result = paypal_service.create_subscription_plan(name, description, amount, currency, interval, current_user)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': 'Subscription plan created successfully',
            'demo_mode': paypal_service.is_demo_mode(current_user)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@paypal_bp.route('/pricing-plans', methods=['GET'])
def get_pricing_plans():
    """Get available pricing plans"""
    try:
        plans = [
            {
                'id': 'starter',
                'name': 'Starter Plan',
                'description': '1,000 AI-generated contents per month',
                'price': 29.99,
                'currency': 'USD',
                'credits': 1000,
                'features': [
                    'OpenAI content generation',
                    'Basic audience analysis',
                    'Email support'
                ]
            },
            {
                'id': 'professional',
                'name': 'Professional Plan',
                'description': '5,000 AI-generated contents per month',
                'price': 79.99,
                'currency': 'USD',
                'credits': 5000,
                'features': [
                    'All Starter features',
                    'Perplexity research',
                    'Claude analysis',
                    'Gemini strategy',
                    'Advanced audience insights',
                    'Priority support'
                ]
            },
            {
                'id': 'enterprise',
                'name': 'Enterprise Plan',
                'description': 'Unlimited AI-generated contents',
                'price': 199.99,
                'currency': 'USD',
                'credits': -1,  # Unlimited
                'features': [
                    'All Professional features',
                    'Unlimited API calls',
                    'Custom integrations',
                    'Dedicated account manager',
                    'White-label options'
                ]
            }
        ]
        
        return jsonify({
            'success': True,
            'data': {'plans': plans},
            'message': 'Pricing plans retrieved successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@paypal_bp.route('/webhook', methods=['POST'])
def paypal_webhook():
    """Handle PayPal webhook notifications"""
    try:
        data = request.get_json()
        event_type = data.get('event_type')
        
        # Handle different webhook events
        if event_type == 'PAYMENT.SALE.COMPLETED':
            # Payment completed successfully
            resource = data.get('resource', {})
            payment_id = resource.get('parent_payment')
            amount = resource.get('amount', {}).get('total')
            
            # Update user credits, send confirmation, etc.
            print(f"Payment completed: {payment_id}, Amount: {amount}")
            
        elif event_type == 'BILLING.SUBSCRIPTION.CREATED':
            # Subscription created
            resource = data.get('resource', {})
            subscription_id = resource.get('id')
            
            print(f"Subscription created: {subscription_id}")
            
        elif event_type == 'BILLING.SUBSCRIPTION.CANCELLED':
            # Subscription cancelled
            resource = data.get('resource', {})
            subscription_id = resource.get('id')
            
            print(f"Subscription cancelled: {subscription_id}")
        
        return jsonify({'status': 'success'}), 200
        
    except Exception as e:
        print(f"Webhook error: {e}")
        return jsonify({'error': 'Webhook processing failed'}), 500

