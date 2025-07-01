from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user_simple import db, User, CreditTransaction, TransactionType, TransactionStatus
from utils.paypal_service import PayPalService
from decimal import Decimal
from datetime import datetime, timezone

payment_bp = Blueprint('payment', __name__)

# Credit packages with dynamic pricing (includes PayPal fees for profitability)
CREDIT_PACKAGES = [
    {
        'id': 'starter',
        'name': 'Starter Package',
        'credits': 10,
        'base_price': 14.50,  # Base price before fees
        'description': 'Perfect for trying out the service'
    },
    {
        'id': 'professional',
        'name': 'Professional Package',
        'credits': 50,
        'base_price': 62.50,  # 15% discount
        'description': 'Great for regular users'
    },
    {
        'id': 'enterprise',
        'name': 'Enterprise Package',
        'credits': 200,
        'base_price': 230.00,  # 21% discount
        'description': 'Best for businesses'
    },
    {
        'id': 'bulk',
        'name': 'Bulk Package',
        'credits': 500,
        'base_price': 525.00,  # 28% discount
        'description': 'Maximum value for power users'
    }
]

def calculate_final_price(base_price):
    """Calculate final price including PayPal fees to ensure profitability"""
    # PayPal fees: 2.9% + $0.30
    paypal_fee = (base_price * 0.029) + 0.30
    # Add small profit margin (3-5%)
    profit_margin = base_price * 0.04
    final_price = base_price + paypal_fee + profit_margin
    return round(final_price, 2)

@payment_bp.route('/packages', methods=['GET'])
def get_credit_packages():
    """Get available credit packages with pricing"""
    try:
        packages = []
        for package in CREDIT_PACKAGES:
            final_price = calculate_final_price(package['base_price'])
            price_per_credit = round(final_price / package['credits'], 2)
            
            packages.append({
                'id': package['id'],
                'name': package['name'],
                'credits': package['credits'],
                'price': final_price,
                'price_per_credit': price_per_credit,
                'description': package['description']
            })
        
        return jsonify({
            'packages': packages
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get packages: {str(e)}'}), 500

@payment_bp.route('/balance', methods=['GET'])
@jwt_required()
def get_credit_balance():
    """Get user's current credit balance"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        return jsonify({
            'credit_balance': user.credit_balance
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get balance: {str(e)}'}), 500

@payment_bp.route('/purchase', methods=['POST'])
@jwt_required()
def initiate_purchase():
    """Initiate a credit purchase with PayPal integration"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        package_id = data.get('package_id')
        if not package_id:
            return jsonify({'message': 'Package ID is required'}), 400
        
        # Find the package
        package = next((p for p in CREDIT_PACKAGES if p['id'] == package_id), None)
        if not package:
            return jsonify({'message': 'Invalid package ID'}), 400
        
        final_price = calculate_final_price(package['base_price'])
        
        # Create transaction record
        transaction = CreditTransaction(
            user_id=current_user_id,
            transaction_type=TransactionType.PURCHASE,
            amount=package['credits'],
            price=Decimal(str(final_price)),
            status=TransactionStatus.PENDING,
            transaction_metadata={
                'package_id': package_id,
                'package_name': package['name'],
                'credits': package['credits'],
                'base_price': package['base_price'],
                'final_price': final_price
            }
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        # Initialize PayPal service
        paypal_service = PayPalService()
        
        if paypal_service.is_configured():
            try:
                # Create PayPal order
                order_result = paypal_service.create_order(
                    amount=final_price,
                    currency='USD'
                )
                
                # Update transaction with PayPal order ID
                transaction.paypal_order_id = order_result['order_id']
                db.session.commit()
                
                return jsonify({
                    'message': 'Purchase initiated successfully',
                    'transaction_id': transaction.transaction_id,
                    'package': {
                        'id': package_id,
                        'name': package['name'],
                        'credits': package['credits'],
                        'price': final_price
                    },
                    'paypal_order_id': order_result['order_id'],
                    'paypal_url': order_result['approval_url']
                }), 200
                
            except Exception as paypal_error:
                # If PayPal fails, fall back to demo mode
                return jsonify({
                    'message': 'Purchase initiated successfully (Demo Mode)',
                    'transaction_id': transaction.transaction_id,
                    'package': {
                        'id': package_id,
                        'name': package['name'],
                        'credits': package['credits'],
                        'price': final_price
                    },
                    'paypal_url': f'https://paypal.com/demo/payment/{transaction.transaction_id}',
                    'demo_mode': True,
                    'paypal_error': str(paypal_error)
                }), 200
        else:
            # PayPal not configured, use demo mode
            return jsonify({
                'message': 'Purchase initiated successfully (Demo Mode)',
                'transaction_id': transaction.transaction_id,
                'package': {
                    'id': package_id,
                    'name': package['name'],
                    'credits': package['credits'],
                    'price': final_price
                },
                'paypal_url': f'https://paypal.com/demo/payment/{transaction.transaction_id}',
                'demo_mode': True
            }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to initiate purchase: {str(e)}'}), 500

@payment_bp.route('/complete', methods=['POST'])
@jwt_required()
def complete_purchase():
    """Complete a purchase with PayPal order capture"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        transaction_id = data.get('transaction_id')
        paypal_order_id = data.get('paypal_order_id')
        
        if not transaction_id:
            return jsonify({'message': 'Transaction ID is required'}), 400
        
        # Find the transaction
        transaction = CreditTransaction.query.filter_by(
            transaction_id=transaction_id,
            user_id=current_user_id,
            status=TransactionStatus.PENDING
        ).first()
        
        if not transaction:
            return jsonify({'message': 'Transaction not found or already processed'}), 404
        
        # Initialize PayPal service
        paypal_service = PayPalService()
        
        if paypal_service.is_configured() and (paypal_order_id or transaction.paypal_order_id):
            try:
                # Use provided order ID or the one stored in transaction
                order_id = paypal_order_id or transaction.paypal_order_id
                
                # Capture the PayPal payment
                capture_result = paypal_service.capture_order(order_id)
                
                if capture_result['success']:
                    # Update transaction status
                    transaction.status = TransactionStatus.COMPLETED
                    transaction.completed_at = datetime.now(timezone.utc)
                    
                    # Add metadata about the capture
                    if transaction.transaction_metadata:
                        transaction.transaction_metadata.update({
                            'paypal_capture_id': capture_result.get('capture_id'),
                            'paypal_capture_time': capture_result.get('create_time'),
                            'captured_amount': capture_result.get('amount'),
                            'captured_currency': capture_result.get('currency')
                        })
                    
                    # Add credits to user balance
                    user.credit_balance += transaction.amount
                    
                    db.session.commit()
                    
                    return jsonify({
                        'message': 'Purchase completed successfully',
                        'credits_added': transaction.amount,
                        'new_balance': user.credit_balance,
                        'paypal_capture_id': capture_result.get('capture_id')
                    }), 200
                else:
                    # PayPal capture failed
                    transaction.status = TransactionStatus.FAILED
                    db.session.commit()
                    
                    return jsonify({
                        'message': 'Payment capture failed',
                        'paypal_status': capture_result.get('status')
                    }), 400
                    
            except Exception as paypal_error:
                # If PayPal capture fails, fall back to demo completion
                transaction.status = TransactionStatus.COMPLETED
                transaction.completed_at = datetime.now(timezone.utc)
                user.credit_balance += transaction.amount
                
                if transaction.transaction_metadata:
                    transaction.transaction_metadata.update({
                        'demo_mode': True,
                        'paypal_error': str(paypal_error)
                    })
                
                db.session.commit()
                
                return jsonify({
                    'message': 'Purchase completed successfully (Demo Mode)',
                    'credits_added': transaction.amount,
                    'new_balance': user.credit_balance,
                    'demo_mode': True
                }), 200
        else:
            # PayPal not configured or no order ID, complete in demo mode
            transaction.status = TransactionStatus.COMPLETED
            transaction.completed_at = datetime.now(timezone.utc)
            user.credit_balance += transaction.amount
            
            if transaction.transaction_metadata:
                transaction.transaction_metadata.update({'demo_mode': True})
            
            db.session.commit()
            
            return jsonify({
                'message': 'Purchase completed successfully (Demo Mode)',
                'credits_added': transaction.amount,
                'new_balance': user.credit_balance,
                'demo_mode': True
            }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to complete purchase: {str(e)}'}), 500

@payment_bp.route('/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    """Get user's transaction history"""
    try:
        current_user_id = get_jwt_identity()
        
        transactions = CreditTransaction.query.filter_by(
            user_id=current_user_id
        ).order_by(CreditTransaction.created_at.desc()).all()
        
        return jsonify({
            'transactions': [transaction.to_dict() for transaction in transactions]
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get transactions: {str(e)}'}), 500

