from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import uuid as python_uuid
import asyncio
from datetime import datetime

from src.models.user import db, User, BusinessType, TargetAudience, AISession, CreditTransaction
from src.utils.multi_ai_service import multi_ai_service

ai_session_bp = Blueprint('ai_session_enhanced', __name__)

@ai_session_bp.route('/sessions', methods=['GET'])
@jwt_required()
def get_sessions():
    """Get all AI sessions for the current user"""
    try:
        user_id = get_jwt_identity()
        
        sessions = AISession.query.filter_by(user_id=user_id).order_by(AISession.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'sessions': [session.to_dict() for session in sessions]
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@ai_session_bp.route('/sessions', methods=['POST'])
@jwt_required()
def create_session():
    """Create a new AI session with multi-AI provider responses"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['business_type_id', 'audience_id', 'mission_objective']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'{field} is required'}), 400
        
        # Verify user has sufficient credits
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404
            
        # Estimate credit cost (5 agents = 5 credits minimum)
        estimated_cost = 5
        if user.credits < estimated_cost:
            return jsonify({
                'success': False, 
                'message': f'Insufficient credits. Need {estimated_cost}, have {user.credits}'
            }), 400
        
        # Get business and audience details
        business = BusinessType.query.get(data['business_type_id'])
        audience = TargetAudience.query.get(data['audience_id'])
        
        if not business:
            return jsonify({'success': False, 'message': 'Business type not found'}), 404
        if not audience:
            return jsonify({'success': False, 'message': 'Target audience not found'}), 404
        
        # Create session record
        session_id = str(python_uuid.uuid4())
        session = AISession(
            session_id=session_id,
            user_id=user_id,
            business_type_id=data['business_type_id'],
            audience_id=data['audience_id'],
            mission_objective=data['mission_objective'],
            status='processing'
        )
        
        db.session.add(session)
        db.session.commit()
        
        # Generate AI responses using multiple providers
        try:
            # Convert SQLAlchemy objects to dicts for the AI service
            business_dict = {
                'name': business.name,
                'description': business.description,
                'industry_category': business.industry_category
            }
            
            audience_dict = {
                'name': audience.name,
                'description': audience.description,
                'manual_description': audience.manual_description
            }
            
            # Call multi-AI service (run async function in sync context)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            ai_result = loop.run_until_complete(
                multi_ai_service.generate_multi_agent_responses(
                    business_dict, 
                    audience_dict, 
                    data['mission_objective']
                )
            )
            loop.close()
            
            # Calculate actual credits consumed based on AI costs
            actual_cost = max(5, int(ai_result['total_cost'] * 100))  # Convert to credits (1 credit = $0.01)
            
            # Check if user still has enough credits after actual calculation
            if user.credits < actual_cost:
                session.status = 'failed'
                session.error_message = f'Insufficient credits for actual cost: {actual_cost}'
                db.session.commit()
                return jsonify({
                    'success': False,
                    'message': f'Insufficient credits. Actual cost: {actual_cost}, available: {user.credits}'
                }), 400
            
            # Deduct credits
            user.credits -= actual_cost
            
            # Record credit transaction
            transaction = CreditTransaction(
                transaction_id=str(python_uuid.uuid4()),
                user_id=user_id,
                transaction_type='consumption',
                amount=-actual_cost,
                description=f'AI Session: {session.mission_objective[:50]}...',
                transaction_metadata={
                    'session_id': session_id,
                    'ai_cost': ai_result['total_cost'],
                    'agents_used': list(ai_result['responses'].keys())
                }
            )
            
            db.session.add(transaction)
            
            # Update session with results
            session.ai_responses = ai_result['responses']
            session.credits_consumed = actual_cost
            session.status = 'completed'
            session.completed_at = datetime.utcnow()
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'session': session.to_dict(),
                'ai_responses': ai_result['responses'],
                'credits_consumed': actual_cost,
                'remaining_credits': user.credits
            })
            
        except Exception as ai_error:
            # Handle AI generation errors
            session.status = 'failed'
            session.error_message = str(ai_error)
            db.session.commit()
            
            return jsonify({
                'success': False,
                'message': f'AI generation failed: {str(ai_error)}'
            }), 500
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@ai_session_bp.route('/sessions/<session_id>', methods=['GET'])
@jwt_required()
def get_session(session_id):
    """Get detailed information about a specific session"""
    try:
        user_id = get_jwt_identity()
        
        session = AISession.query.filter_by(
            session_id=session_id,
            user_id=user_id
        ).first()
        
        if not session:
            return jsonify({'success': False, 'message': 'Session not found'}), 404
        
        return jsonify({
            'success': True,
            'session': session.to_dict()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@ai_session_bp.route('/sessions/<session_id>/regenerate', methods=['POST'])
@jwt_required()
def regenerate_responses(session_id):
    """Regenerate AI responses for a specific session"""
    try:
        user_id = get_jwt_identity()
        
        session = AISession.query.filter_by(
            session_id=session_id,
            user_id=user_id
        ).first()
        
        if not session:
            return jsonify({'success': False, 'message': 'Session not found'}), 404
        
        user = User.query.get(user_id)
        
        # Estimate cost for regeneration
        estimated_cost = 5
        if user.credits < estimated_cost:
            return jsonify({
                'success': False,
                'message': f'Insufficient credits for regeneration. Need {estimated_cost}, have {user.credits}'
            }), 400
        
        # Get business and audience details
        business = BusinessType.query.get(session.business_type_id)
        audience = TargetAudience.query.get(session.audience_id)
        
        # Regenerate responses
        business_dict = {
            'name': business.name,
            'description': business.description,
            'industry_category': business.industry_category
        }
        
        audience_dict = {
            'name': audience.name,
            'description': audience.description,
            'manual_description': audience.manual_description
        }
        
        # Call multi-AI service
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        ai_result = loop.run_until_complete(
            multi_ai_service.generate_multi_agent_responses(
                business_dict,
                audience_dict,
                session.mission_objective
            )
        )
        loop.close()
        
        # Calculate actual cost
        actual_cost = max(5, int(ai_result['total_cost'] * 100))
        
        if user.credits < actual_cost:
            return jsonify({
                'success': False,
                'message': f'Insufficient credits. Actual cost: {actual_cost}, available: {user.credits}'
            }), 400
        
        # Deduct credits
        user.credits -= actual_cost
        
        # Record transaction
        transaction = CreditTransaction(
            transaction_id=str(python_uuid.uuid4()),
            user_id=user_id,
            transaction_type='consumption',
            amount=-actual_cost,
            description=f'Regenerate Session: {session.mission_objective[:50]}...',
            transaction_metadata={
                'session_id': session_id,
                'ai_cost': ai_result['total_cost'],
                'regeneration': True
            }
        )
        
        db.session.add(transaction)
        
        # Update session
        session.ai_responses = ai_result['responses']
        session.credits_consumed += actual_cost
        session.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'ai_responses': ai_result['responses'],
            'credits_consumed': actual_cost,
            'remaining_credits': user.credits
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@ai_session_bp.route('/agents/info', methods=['GET'])
def get_agent_info():
    """Get information about available AI agents and their providers"""
    try:
        agent_info = multi_ai_service.get_agent_info()
        
        return jsonify({
            'success': True,
            'agents': agent_info
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

