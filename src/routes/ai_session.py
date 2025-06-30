from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import db, User, BusinessType, TargetAudience, AISession, SessionStatus
from src.utils.ai_service import AIService
from datetime import datetime, timezone
import uuid as python_uuid

ai_session_bp = Blueprint('ai_session', __name__)

@ai_session_bp.route('/sessions', methods=['POST'])
@jwt_required()
def create_session():
    """Create a new AI persuasion session."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['business_type_id', 'audience_id', 'mission_objective']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'{field} is required'}), 400
        
        # Get business type and audience
        business_type = BusinessType.query.get(data['business_type_id'])
        target_audience = TargetAudience.query.get(data['audience_id'])
        
        if not business_type:
            return jsonify({'message': 'Business type not found'}), 404
        
        if not target_audience:
            return jsonify({'message': 'Target audience not found'}), 404
        
        # Initialize AI service
        ai_service = AIService()
        
        # Calculate credit cost
        session_data = {
            'mission_objective': data['mission_objective'],
            'business_type': business_type.to_dict(),
            'target_audience': target_audience.to_dict()
        }
        credit_cost = ai_service.calculate_credit_cost(session_data)
        
        # Check if user has enough credits
        if user.credit_balance < credit_cost:
            return jsonify({
                'message': 'Insufficient credits',
                'required_credits': credit_cost,
                'current_balance': float(user.credit_balance)
            }), 402  # Payment Required
        
        # Generate AI responses
        try:
            ai_responses = ai_service.generate_persuasion_responses(
                business_type=business_type.to_dict(),
                target_audience=target_audience.to_dict(),
                mission_objective=data['mission_objective']
            )
        except Exception as e:
            return jsonify({
                'message': f'AI generation failed: {str(e)}',
                'fallback': 'Using template-based responses'
            }), 500
        
        # Create session record
        session = AISession(
            user_id=current_user_id,
            business_type_id=data['business_type_id'],
            audience_id=data['audience_id'],
            mission_objective=data['mission_objective'],
            credits_consumed=credit_cost,
            status=SessionStatus.ACTIVE,
            ai_responses=ai_responses,
            session_metadata={
                'ai_model_used': ai_service.get_available_models()[0] if ai_service.get_available_models() else 'template',
                'generation_timestamp': datetime.now(timezone.utc).isoformat(),
                'business_context': business_type.name,
                'audience_context': target_audience.name
            }
        )
        
        # Deduct credits from user
        user.deduct_credits(credit_cost)
        
        # Save to database
        db.session.add(session)
        db.session.commit()
        
        return jsonify({
            'message': 'AI session created successfully',
            'session': session.to_dict(),
            'ai_responses': ai_responses,
            'credits_consumed': credit_cost,
            'remaining_balance': float(user.credit_balance)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to create session: {str(e)}'}), 500

@ai_session_bp.route('/sessions', methods=['GET'])
@jwt_required()
def get_sessions():
    """Get user's AI sessions."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        # Get query parameters
        status = request.args.get('status')
        limit = request.args.get('limit', 10, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Build query
        query = AISession.query.filter_by(user_id=current_user_id)
        
        if status:
            try:
                status_enum = SessionStatus(status)
                query = query.filter_by(status=status_enum)
            except ValueError:
                return jsonify({'message': 'Invalid status'}), 400
        
        # Order by creation date (newest first)
        query = query.order_by(AISession.created_at.desc())
        
        # Apply pagination
        total = query.count()
        sessions = query.offset(offset).limit(limit).all()
        
        # Include related data
        session_data = []
        for session in sessions:
            session_dict = session.to_dict()
            
            # Add business type info
            if session.business_type:
                session_dict['business_type'] = session.business_type.to_dict()
            
            # Add target audience info
            if session.target_audience:
                session_dict['target_audience'] = session.target_audience.to_dict()
            
            session_data.append(session_dict)
        
        return jsonify({
            'sessions': session_data,
            'total': total,
            'limit': limit,
            'offset': offset,
            'has_more': offset + len(sessions) < total
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get sessions: {str(e)}'}), 500

@ai_session_bp.route('/sessions/<session_id>', methods=['GET'])
@jwt_required()
def get_session(session_id):
    """Get a specific AI session with full details."""
    try:
        current_user_id = get_jwt_identity()
        
        session = AISession.query.filter_by(
            session_id=session_id,
            user_id=current_user_id
        ).first()
        
        if not session:
            return jsonify({'message': 'Session not found'}), 404
        
        # Build detailed response
        session_dict = session.to_dict()
        
        # Add business type info
        if session.business_type:
            session_dict['business_type'] = session.business_type.to_dict()
        
        # Add target audience info
        if session.target_audience:
            session_dict['target_audience'] = session.target_audience.to_dict()
        
        # Add AI responses if available
        if session.ai_responses:
            session_dict['ai_responses'] = session.ai_responses
        
        return jsonify({
            'session': session_dict
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get session: {str(e)}'}), 500

@ai_session_bp.route('/sessions/<session_id>/regenerate', methods=['POST'])
@jwt_required()
def regenerate_responses(session_id):
    """Regenerate AI responses for a session."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        session = AISession.query.filter_by(
            session_id=session_id,
            user_id=current_user_id
        ).first()
        
        if not session:
            return jsonify({'message': 'Session not found'}), 404
        
        # Calculate regeneration cost (50% of original cost)
        ai_service = AIService()
        session_data = {
            'mission_objective': session.mission_objective,
            'business_type': session.business_type.to_dict() if session.business_type else {},
            'target_audience': session.target_audience.to_dict() if session.target_audience else {}
        }
        regeneration_cost = ai_service.calculate_credit_cost(session_data) * 0.5
        
        # Check if user has enough credits
        if user.credit_balance < regeneration_cost:
            return jsonify({
                'message': 'Insufficient credits for regeneration',
                'required_credits': regeneration_cost,
                'current_balance': float(user.credit_balance)
            }), 402
        
        # Generate new AI responses
        try:
            new_responses = ai_service.generate_persuasion_responses(
                business_type=session.business_type.to_dict() if session.business_type else {},
                target_audience=session.target_audience.to_dict() if session.target_audience else {},
                mission_objective=session.mission_objective
            )
        except Exception as e:
            return jsonify({
                'message': f'AI regeneration failed: {str(e)}'
            }), 500
        
        # Update session
        session.ai_responses = new_responses
        session.credits_consumed += regeneration_cost
        session.message_count = (session.message_count or 0) + 1
        
        # Update metadata
        if session.session_metadata:
            session.session_metadata['last_regeneration'] = datetime.now(timezone.utc).isoformat()
            session.session_metadata['total_regenerations'] = session.session_metadata.get('total_regenerations', 0) + 1
        
        # Deduct credits
        user.deduct_credits(regeneration_cost)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Responses regenerated successfully',
            'ai_responses': new_responses,
            'credits_consumed': regeneration_cost,
            'remaining_balance': float(user.credit_balance)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to regenerate responses: {str(e)}'}), 500

@ai_session_bp.route('/sessions/<session_id>/status', methods=['PUT'])
@jwt_required()
def update_session_status(session_id):
    """Update session status."""
    try:
        current_user_id = get_jwt_identity()
        
        data = request.get_json()
        if not data or 'status' not in data:
            return jsonify({'message': 'Status is required'}), 400
        
        session = AISession.query.filter_by(
            session_id=session_id,
            user_id=current_user_id
        ).first()
        
        if not session:
            return jsonify({'message': 'Session not found'}), 404
        
        try:
            new_status = SessionStatus(data['status'])
            session.status = new_status
            db.session.commit()
            
            return jsonify({
                'message': 'Session status updated',
                'session_id': session_id,
                'new_status': new_status.value
            }), 200
            
        except ValueError:
            return jsonify({'message': 'Invalid status value'}), 400
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to update status: {str(e)}'}), 500

@ai_session_bp.route('/sessions/stats', methods=['GET'])
@jwt_required()
def get_session_stats():
    """Get user's session statistics."""
    try:
        current_user_id = get_jwt_identity()
        
        # Get session counts by status
        total_sessions = AISession.query.filter_by(user_id=current_user_id).count()
        active_sessions = AISession.query.filter_by(
            user_id=current_user_id,
            status=SessionStatus.ACTIVE
        ).count()
        completed_sessions = AISession.query.filter_by(
            user_id=current_user_id,
            status=SessionStatus.COMPLETED
        ).count()
        
        # Get total credits consumed
        total_credits_consumed = db.session.query(
            db.func.sum(AISession.credits_consumed)
        ).filter_by(user_id=current_user_id).scalar() or 0
        
        # Get recent activity
        recent_sessions = AISession.query.filter_by(
            user_id=current_user_id
        ).order_by(AISession.created_at.desc()).limit(5).all()
        
        return jsonify({
            'stats': {
                'total_sessions': total_sessions,
                'active_sessions': active_sessions,
                'completed_sessions': completed_sessions,
                'total_credits_consumed': float(total_credits_consumed)
            },
            'recent_activity': [session.to_dict() for session in recent_sessions]
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get stats: {str(e)}'}), 500

@ai_session_bp.route('/ai-models', methods=['GET'])
def get_available_models():
    """Get list of available AI models."""
    try:
        ai_service = AIService()
        models = ai_service.get_available_models()
        
        return jsonify({
            'models': models,
            'configured': ai_service.is_configured()
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get models: {str(e)}'}), 500

