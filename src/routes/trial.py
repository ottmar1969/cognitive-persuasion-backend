from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from src.models.user_simple import db, User
from src.models.free_trial import FreeTrialManager

trial_bp = Blueprint('trial', __name__)

@trial_bp.route('/status', methods=['GET'])
@jwt_required()
def get_trial_status():
    """Get current trial status for user"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        status = FreeTrialManager.get_trial_status(user)
        
        return jsonify({
            'success': True,
            'trial_status': status
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@trial_bp.route('/start', methods=['POST'])
@jwt_required()
def start_trial():
    """Start free trial for user"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        if not FreeTrialManager.is_trial_eligible(user):
            return jsonify({
                'success': False, 
                'message': 'User not eligible for trial'
            }), 400
        
        success = FreeTrialManager.start_trial(user)
        
        if success:
            status = FreeTrialManager.get_trial_status(user)
            return jsonify({
                'success': True,
                'message': 'Trial started successfully',
                'trial_status': status
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to start trial'
            }), 400
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@trial_bp.route('/session/use', methods=['POST'])
@jwt_required()
def use_trial_session():
    """Use one trial session"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        if not FreeTrialManager.is_trial_active(user):
            return jsonify({
                'success': False,
                'message': 'No active trial or trial expired'
            }), 400
        
        success = FreeTrialManager.use_trial_session(user)
        
        if success:
            status = FreeTrialManager.get_trial_status(user)
            return jsonify({
                'success': True,
                'message': 'Trial session used',
                'trial_status': status
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to use trial session'
            }), 400
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@trial_bp.route('/extend', methods=['POST'])
@jwt_required()
def extend_trial():
    """Extend trial (for promotions, referrals, etc.)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        data = request.get_json()
        
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        additional_sessions = data.get('additional_sessions', 0)
        
        success = FreeTrialManager.extend_trial(user, additional_sessions=additional_sessions)
        
        if success:
            status = FreeTrialManager.get_trial_status(user)
            return jsonify({
                'success': True,
                'message': f'Trial extended by {additional_sessions} sessions',
                'trial_status': status
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to extend trial'
            }), 400
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@trial_bp.route('/info', methods=['GET'])
def get_trial_info():
    """Get trial information for marketing/landing page"""
    try:
        return jsonify({
            'success': True,
            'trial_info': {
                'duration_minutes': FreeTrialManager.TRIAL_DURATION_MINUTES,
                'sessions_included': FreeTrialManager.TRIAL_SESSIONS_LIMIT,
                'businesses_limit': FreeTrialManager.TRIAL_BUSINESSES_LIMIT,
                'audiences_limit': FreeTrialManager.TRIAL_AUDIENCES_LIMIT,
                'features_included': [
                    'All 5 AI agents (OpenAI, Gemini, Claude, Perplexity)',
                    'Complete business analysis',
                    'Multiple audience targeting',
                    'Professional persuasion strategies',
                    'Copy-to-clipboard functionality',
                    'Response regeneration'
                ],
                'value_proposition': '3-Minute Power Demo - Experience the full system instantly!',
                'upgrade_incentive': '50% off first month when you upgrade during trial'
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

