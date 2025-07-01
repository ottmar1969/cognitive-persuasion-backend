from flask import Blueprint, request, jsonify, current_app
from models.user_simple import db, CreditTransaction, TransactionStatus, User
from utils.paypal_service import PayPalService
from datetime import datetime, timezone
import json

webhook_bp = Blueprint('paypal_webhook', __name__)

@webhook_bp.route('/paypal/webhook', methods=['POST'])
def handle_paypal_webhook():
    """Handle PayPal webhook notifications for payment events."""
    try:
        # Get webhook data
        webhook_data = request.get_json()
        headers = request.headers
        
        if not webhook_data:
            return jsonify({'message': 'No webhook data received'}), 400
        
        # Initialize PayPal service
        paypal_service = PayPalService()
        
        if not paypal_service.is_configured():
            current_app.logger.warning("PayPal webhook received but service not configured")
            return jsonify({'message': 'PayPal service not configured'}), 400
        
        # Get webhook ID from config
        webhook_id = current_app.config.get('PAYPAL_WEBHOOK_ID')
        
        # Verify webhook signature if webhook ID is configured
        if webhook_id:
            is_valid = paypal_service.verify_webhook_signature(
                headers, 
                request.get_data(as_text=True), 
                webhook_id
            )
            
            if not is_valid:
                current_app.logger.warning("Invalid PayPal webhook signature")
                return jsonify({'message': 'Invalid webhook signature'}), 401
        
        # Process webhook event
        event_type = webhook_data.get('event_type')
        resource = webhook_data.get('resource', {})
        
        current_app.logger.info(f"Processing PayPal webhook: {event_type}")
        
        if event_type == 'CHECKOUT.ORDER.APPROVED':
            # Order approved by customer
            order_id = resource.get('id')
            if order_id:
                handle_order_approved(order_id, webhook_data)
        
        elif event_type == 'PAYMENT.CAPTURE.COMPLETED':
            # Payment captured successfully
            capture_id = resource.get('id')
            order_id = resource.get('supplementary_data', {}).get('related_ids', {}).get('order_id')
            if capture_id and order_id:
                handle_payment_captured(order_id, capture_id, webhook_data)
        
        elif event_type == 'PAYMENT.CAPTURE.DENIED':
            # Payment capture denied
            order_id = resource.get('supplementary_data', {}).get('related_ids', {}).get('order_id')
            if order_id:
                handle_payment_denied(order_id, webhook_data)
        
        elif event_type == 'CHECKOUT.ORDER.COMPLETED':
            # Order completed
            order_id = resource.get('id')
            if order_id:
                handle_order_completed(order_id, webhook_data)
        
        return jsonify({'message': 'Webhook processed successfully'}), 200
        
    except Exception as e:
        current_app.logger.error(f"PayPal webhook processing failed: {str(e)}")
        return jsonify({'message': 'Webhook processing failed'}), 500

def handle_order_approved(order_id, webhook_data):
    """Handle order approved event."""
    try:
        # Find transaction by PayPal order ID
        transaction = CreditTransaction.query.filter_by(
            paypal_order_id=order_id,
            status=TransactionStatus.PENDING
        ).first()
        
        if transaction:
            # Update transaction metadata
            if transaction.transaction_metadata:
                transaction.transaction_metadata.update({
                    'paypal_approved_at': datetime.now(timezone.utc).isoformat(),
                    'webhook_event': 'ORDER.APPROVED'
                })
            
            db.session.commit()
            current_app.logger.info(f"Order approved: {order_id}")
        
    except Exception as e:
        current_app.logger.error(f"Failed to handle order approved: {str(e)}")

def handle_payment_captured(order_id, capture_id, webhook_data):
    """Handle payment capture completed event."""
    try:
        # Find transaction by PayPal order ID
        transaction = CreditTransaction.query.filter_by(
            paypal_order_id=order_id,
            status=TransactionStatus.PENDING
        ).first()
        
        if transaction:
            # Update transaction status
            transaction.status = TransactionStatus.COMPLETED
            transaction.completed_at = datetime.now(timezone.utc)
            
            # Update metadata
            if transaction.transaction_metadata:
                transaction.transaction_metadata.update({
                    'paypal_capture_id': capture_id,
                    'paypal_captured_at': datetime.now(timezone.utc).isoformat(),
                    'webhook_event': 'PAYMENT.CAPTURE.COMPLETED'
                })
            
            # Add credits to user balance
            user = User.query.get(transaction.user_id)
            if user:
                user.credit_balance += transaction.amount
            
            db.session.commit()
            current_app.logger.info(f"Payment captured: {order_id}, credits added: {transaction.amount}")
        
    except Exception as e:
        current_app.logger.error(f"Failed to handle payment captured: {str(e)}")
        db.session.rollback()

def handle_payment_denied(order_id, webhook_data):
    """Handle payment capture denied event."""
    try:
        # Find transaction by PayPal order ID
        transaction = CreditTransaction.query.filter_by(
            paypal_order_id=order_id,
            status=TransactionStatus.PENDING
        ).first()
        
        if transaction:
            # Update transaction status
            transaction.status = TransactionStatus.FAILED
            
            # Update metadata
            if transaction.transaction_metadata:
                transaction.transaction_metadata.update({
                    'paypal_denied_at': datetime.now(timezone.utc).isoformat(),
                    'webhook_event': 'PAYMENT.CAPTURE.DENIED'
                })
            
            db.session.commit()
            current_app.logger.info(f"Payment denied: {order_id}")
        
    except Exception as e:
        current_app.logger.error(f"Failed to handle payment denied: {str(e)}")

def handle_order_completed(order_id, webhook_data):
    """Handle order completed event."""
    try:
        # Find transaction by PayPal order ID
        transaction = CreditTransaction.query.filter_by(
            paypal_order_id=order_id
        ).first()
        
        if transaction:
            # Update metadata
            if transaction.transaction_metadata:
                transaction.transaction_metadata.update({
                    'paypal_completed_at': datetime.now(timezone.utc).isoformat(),
                    'webhook_event': 'ORDER.COMPLETED'
                })
            
            db.session.commit()
            current_app.logger.info(f"Order completed: {order_id}")
        
    except Exception as e:
        current_app.logger.error(f"Failed to handle order completed: {str(e)}")

@webhook_bp.route('/paypal/webhook/test', methods=['GET'])
def test_webhook():
    """Test endpoint to verify webhook configuration."""
    try:
        paypal_service = PayPalService()
        config_status = paypal_service.get_configuration_status()
        
        return jsonify({
            'message': 'PayPal webhook endpoint is active',
            'configuration': config_status,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'message': 'Webhook test failed',
            'error': str(e)
        }), 500

