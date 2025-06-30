from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user_simple import db, User, CreditTransaction, TransactionType, TransactionStatus
from decimal import Decimal

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
    """Initiate a credit purchase (simplified for demo)"""
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
        
        # In a real implementation, this would integrate with PayPal API
        # For demo purposes, we'll simulate a successful payment
        return jsonify({
            'message': 'Purchase initiated successfully',
            'transaction_id': transaction.transaction_id,
            'package': {
                'id': package_id,
                'name': package['name'],
                'credits': package['credits'],
                'price': final_price
            },
            'paypal_url': f'https://paypal.com/demo/payment/{transaction.transaction_id}'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to initiate purchase: {str(e)}'}), 500

@payment_bp.route('/complete', methods=['POST'])
@jwt_required()
def complete_purchase():
    """Complete a purchase (simplified for demo)"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        transaction_id = data.get('transaction_id')
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
        
        # Update transaction status
        transaction.status = TransactionStatus.COMPLETED
        
        # Add credits to user balance
        user.credit_balance += transaction.amount
        
        db.session.commit()
        
        return jsonify({
            'message': 'Purchase completed successfully',
            'credits_added': transaction.amount,
            'new_balance': user.credit_balance
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

