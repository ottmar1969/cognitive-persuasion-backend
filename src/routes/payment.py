from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import db, User, CreditTransaction, TransactionType, TransactionStatus
from src.utils.paypal_service import PayPalService
from decimal import Decimal
import uuid as python_uuid

payment_bp = Blueprint('payment', __name__)

# Credit packages with dynamic pricing
CREDIT_PACKAGES = {
    'starter': {
        'credits': 10,
        'base_price': 15.00,
        'name': 'Starter Package',
        'description': '10 credits for new users and small projects'
    },
    'professional': {
        'credits': 50,
        'base_price': 65.00,
        'name': 'Professional Package',
        'description': '50 credits for regular users and growing businesses'
    },
    'enterprise': {
        'credits': 200,
        'base_price': 240.00,
        'name': 'Enterprise Package',
        'description': '200 credits for high-volume users and agencies'
    },
    'bulk': {
        'credits': 500,
        'base_price': 550.00,
        'name': 'Bulk Package',
        'description': '500 credits for enterprise clients and resellers'
    }
}

def calculate_final_price(base_price):
    """Calculate final price including PayPal fees to ensure profitability."""
    # PayPal fees: 2.9% + $0.30 for domestic transactions
    paypal_percentage_fee = 0.029
    paypal_fixed_fee = 0.30
    
    # Calculate price that covers PayPal fees
    # Formula: (base_price + fixed_fee) / (1 - percentage_fee)
    price_with_fees = (base_price + paypal_fixed_fee) / (1 - paypal_percentage_fee)
    
    # Round to 2 decimal places
    return round(price_with_fees, 2)

@payment_bp.route('/packages', methods=['GET'])
def get_credit_packages():
    """Get available credit packages with current pricing."""
    try:
        packages = {}
        
        for package_id, package_info in CREDIT_PACKAGES.items():
            base_price = package_info['base_price']
            final_price = calculate_final_price(base_price)
            
            packages[package_id] = {
                'credits': package_info['credits'],
                'price': final_price,
                'base_price': base_price,
                'name': package_info['name'],
                'description': package_info['description'],
                'price_per_credit': round(final_price / package_info['credits'], 2),
                'savings_vs_starter': 0
            }
        
        # Calculate savings compared to starter package
        starter_per_credit = packages['starter']['price_per_credit']
        for package_id, package_data in packages.items():
            if package_id != 'starter':
                savings_percent = ((starter_per_credit - package_data['price_per_credit']) / starter_per_credit) * 100
                package_data['savings_vs_starter'] = round(max(0, savings_percent), 1)
        
        return jsonify({
            'packages': packages,
            'currency': 'USD',
            'note': 'Prices include PayPal processing fees'
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get packages: {str(e)}'}), 500

@payment_bp.route('/purchase', methods=['POST'])
@jwt_required()
def initiate_purchase():
    """Initiate a credit purchase via PayPal."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        package_id = data.get('package_id')
        
        if package_id not in CREDIT_PACKAGES:
            return jsonify({'message': 'Invalid package selected'}), 400
        
        package_info = CREDIT_PACKAGES[package_id]
        final_price = calculate_final_price(package_info['base_price'])
        
        # Create pending transaction record
        transaction = CreditTransaction(
            user_id=current_user_id,
            amount=Decimal(str(package_info['credits'])),  # Amount in credits
            transaction_type=TransactionType.PURCHASE,
            status=TransactionStatus.PENDING,
            transaction_metadata={
                'package_id': package_id,
                'package_name': package_info['name'],
                'price_usd': final_price,
                'base_price_usd': package_info['base_price']
            }
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        # Initialize PayPal service
        paypal_service = PayPalService()
        
        try:
            # Create PayPal payment
            payment_data = paypal_service.create_payment(
                amount=final_price,
                currency='USD',
                description=f"{package_info['name']} - {package_info['credits']} credits",
                return_url=f"{request.host_url}api/payments/success",
                cancel_url=f"{request.host_url}api/payments/cancel",
                custom_data=transaction.transaction_id
            )
            
            if payment_data and 'approval_url' in payment_data:
                # Update transaction with PayPal payment ID
                transaction.paypal_transaction_id = payment_data['payment_id']
                db.session.commit()
                
                return jsonify({
                    'message': 'Payment initiated successfully',
                    'approval_url': payment_data['approval_url'],
                    'payment_id': payment_data['payment_id'],
                    'transaction_id': transaction.transaction_id,
                    'package': {
                        'name': package_info['name'],
                        'credits': package_info['credits'],
                        'price': final_price
                    }
                }), 200
            else:
                # PayPal payment creation failed
                transaction.fail_transaction()
                return jsonify({'message': 'Failed to create PayPal payment'}), 500
                
        except Exception as e:
            transaction.fail_transaction()
            return jsonify({'message': f'PayPal integration error: {str(e)}'}), 500
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to initiate purchase: {str(e)}'}), 500

@payment_bp.route('/success', methods=['GET'])
def payment_success():
    """Handle successful PayPal payment."""
    try:
        payment_id = request.args.get('paymentId')
        payer_id = request.args.get('PayerID')
        
        if not payment_id or not payer_id:
            return jsonify({'message': 'Missing payment parameters'}), 400
        
        # Find transaction by PayPal payment ID
        transaction = CreditTransaction.query.filter_by(
            paypal_transaction_id=payment_id,
            status=TransactionStatus.PENDING
        ).first()
        
        if not transaction:
            return jsonify({'message': 'Transaction not found'}), 404
        
        # Initialize PayPal service
        paypal_service = PayPalService()
        
        try:
            # Execute PayPal payment
            execution_result = paypal_service.execute_payment(payment_id, payer_id)
            
            if execution_result and execution_result.get('state') == 'approved':
                # Payment successful - add credits to user account
                user = User.query.get(transaction.user_id)
                if user:
                    credits_to_add = float(transaction.amount)
                    user.add_credits(credits_to_add)
                    
                    # Update transaction
                    transaction.complete_transaction()
                    transaction.paypal_fee = Decimal(str(execution_result.get('paypal_fee', 0)))
                    transaction.net_amount = transaction.amount - (transaction.paypal_fee or 0)
                    
                    # Update metadata with execution details
                    if transaction.transaction_metadata:
                        transaction.transaction_metadata.update({
                            'payer_id': payer_id,
                            'execution_time': execution_result.get('create_time'),
                            'payment_method': execution_result.get('payment_method')
                        })
                    
                    db.session.commit()
                    
                    return jsonify({
                        'message': 'Payment completed successfully',
                        'credits_added': credits_to_add,
                        'new_balance': float(user.credit_balance),
                        'transaction_id': transaction.transaction_id
                    }), 200
                else:
                    return jsonify({'message': 'User not found'}), 404
            else:
                # Payment execution failed
                transaction.fail_transaction()
                return jsonify({'message': 'Payment execution failed'}), 400
                
        except Exception as e:
            transaction.fail_transaction()
            return jsonify({'message': f'Payment execution error: {str(e)}'}), 500
        
    except Exception as e:
        return jsonify({'message': f'Payment processing error: {str(e)}'}), 500

@payment_bp.route('/cancel', methods=['GET'])
def payment_cancel():
    """Handle cancelled PayPal payment."""
    try:
        payment_id = request.args.get('paymentId')
        
        if payment_id:
            # Find and mark transaction as failed
            transaction = CreditTransaction.query.filter_by(
                paypal_transaction_id=payment_id,
                status=TransactionStatus.PENDING
            ).first()
            
            if transaction:
                transaction.fail_transaction()
        
        return jsonify({
            'message': 'Payment was cancelled',
            'payment_id': payment_id
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error handling cancellation: {str(e)}'}), 500

@payment_bp.route('/webhook', methods=['POST'])
def paypal_webhook():
    """Handle PayPal webhook notifications."""
    try:
        # PayPal webhook verification would go here
        # For now, we'll just log the webhook data
        webhook_data = request.get_json()
        
        if webhook_data:
            event_type = webhook_data.get('event_type')
            
            # Handle different webhook events
            if event_type == 'PAYMENT.SALE.COMPLETED':
                # Handle completed payment
                pass
            elif event_type == 'PAYMENT.SALE.DENIED':
                # Handle denied payment
                pass
            elif event_type == 'PAYMENT.SALE.REFUNDED':
                # Handle refunded payment
                pass
        
        return jsonify({'message': 'Webhook processed'}), 200
        
    except Exception as e:
        return jsonify({'message': f'Webhook error: {str(e)}'}), 500

@payment_bp.route('/balance', methods=['GET'])
@jwt_required()
def get_credit_balance():
    """Get current user's credit balance."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        return jsonify({
            'credit_balance': float(user.credit_balance),
            'total_spent': float(user.total_spent),
            'user_id': user.user_id
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get balance: {str(e)}'}), 500

@payment_bp.route('/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    """Get user's transaction history."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        # Get query parameters
        transaction_type = request.args.get('type')
        status = request.args.get('status')
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Build query
        query = CreditTransaction.query.filter_by(user_id=current_user_id)
        
        if transaction_type:
            try:
                type_enum = TransactionType(transaction_type)
                query = query.filter_by(transaction_type=type_enum)
            except ValueError:
                return jsonify({'message': 'Invalid transaction type'}), 400
        
        if status:
            try:
                status_enum = TransactionStatus(status)
                query = query.filter_by(status=status_enum)
            except ValueError:
                return jsonify({'message': 'Invalid status'}), 400
        
        # Order by creation date (newest first)
        query = query.order_by(CreditTransaction.created_at.desc())
        
        # Apply pagination
        total = query.count()
        transactions = query.offset(offset).limit(limit).all()
        
        return jsonify({
            'transactions': [txn.to_dict() for txn in transactions],
            'total': total,
            'limit': limit,
            'offset': offset,
            'has_more': offset + len(transactions) < total
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get transactions: {str(e)}'}), 500

@payment_bp.route('/pricing-calculator', methods=['GET'])
def pricing_calculator():
    """Get pricing calculation details for transparency."""
    try:
        base_price = request.args.get('base_price', type=float)
        
        if not base_price or base_price <= 0:
            return jsonify({'message': 'Valid base price is required'}), 400
        
        # PayPal fee structure
        paypal_percentage_fee = 0.029  # 2.9%
        paypal_fixed_fee = 0.30
        
        # Calculate breakdown
        final_price = calculate_final_price(base_price)
        total_paypal_fee = (final_price * paypal_percentage_fee) + paypal_fixed_fee
        net_amount = final_price - total_paypal_fee
        
        return jsonify({
            'base_price': base_price,
            'final_price': final_price,
            'paypal_fees': {
                'percentage_fee': paypal_percentage_fee * 100,  # Show as percentage
                'fixed_fee': paypal_fixed_fee,
                'total_fee': round(total_paypal_fee, 2)
            },
            'net_amount': round(net_amount, 2),
            'markup': round(final_price - base_price, 2),
            'markup_percentage': round(((final_price - base_price) / base_price) * 100, 1)
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Calculation error: {str(e)}'}), 500

