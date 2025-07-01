from flask import Blueprint, request, jsonify
from models.user_simple import db, TargetAudience

audience_bp = Blueprint('audience', __name__)

@audience_bp.route('', methods=['GET'])
def get_target_audiences():
    """Get all target audiences (predefined + session-based custom)"""
    try:
        # Get session fingerprint from request
        session_id = getattr(request, 'fingerprint', 'anonymous')
        
        # Get predefined audiences (user_id is None) and session's custom audiences
        audiences = TargetAudience.query.filter(
            (TargetAudience.user_id == session_id) | (TargetAudience.user_id == None)
        ).all()
        
        return jsonify({
            'target_audiences': [audience.to_dict() for audience in audiences],
            'session_id': session_id
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get target audiences: {str(e)}'}), 500

@audience_bp.route('/manual', methods=['POST'])
def create_manual_audience():
    """Create a new manual target audience"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        # Get session fingerprint from request
        session_id = getattr(request, 'fingerprint', 'anonymous')
        
        manual_description = data.get('manual_description', '').strip()
        name = data.get('name', '').strip()
        
        if not manual_description:
            return jsonify({'message': 'Manual description is required'}), 400
        
        # Generate name if not provided
        if not name:
            # Create a name from the first few words of the description
            words = manual_description.split()[:3]
            name = ' '.join(words).title()
            if len(name) > 50:
                name = name[:47] + '...'
        
        # Check if audience already exists for this session
        existing = TargetAudience.query.filter_by(
            name=name,
            user_id=session_id
        ).first()
        
        if existing:
            return jsonify({'message': 'Audience with this name already exists'}), 409
        
        # Create new target audience
        audience = TargetAudience(
            name=name,
            description=manual_description,
            user_id=session_id,  # Use session fingerprint instead of user_id
            is_predefined=False
        )
        
        db.session.add(audience)
        db.session.commit()
        
        return jsonify({
            'message': 'Target audience created successfully',
            'target_audience': audience.to_dict(),
            'session_id': session_id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to create target audience: {str(e)}'}), 500

@audience_bp.route('', methods=['POST'])
def create_audience():
    """Create a new target audience"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        # Get session fingerprint from request
        session_id = getattr(request, 'fingerprint', 'anonymous')
        
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        
        if not name:
            return jsonify({'message': 'Audience name is required'}), 400
        
        if not description:
            return jsonify({'message': 'Audience description is required'}), 400
        
        # Check if audience already exists for this session
        existing = TargetAudience.query.filter_by(
            name=name,
            user_id=session_id
        ).first()
        
        if existing:
            return jsonify({'message': 'Audience with this name already exists'}), 409
        
        # Create new target audience
        audience = TargetAudience(
            name=name,
            description=description,
            user_id=session_id,  # Use session fingerprint instead of user_id
            is_predefined=False
        )
        
        db.session.add(audience)
        db.session.commit()
        
        return jsonify({
            'message': 'Target audience created successfully',
            'target_audience': audience.to_dict(),
            'session_id': session_id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to create target audience: {str(e)}'}), 500

@audience_bp.route('/<int:audience_id>', methods=['PUT'])
def update_audience(audience_id):
    """Update a target audience"""
    try:
        # Get session fingerprint from request
        session_id = getattr(request, 'fingerprint', 'anonymous')
        
        audience = TargetAudience.query.filter_by(
            audience_id=audience_id,
            user_id=session_id
        ).first()
        
        if not audience:
            return jsonify({'message': 'Audience not found or access denied'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        # Update fields if provided
        if 'name' in data:
            name = data['name'].strip()
            if not name:
                return jsonify({'message': 'Audience name cannot be empty'}), 400
            audience.name = name
        
        if 'description' in data:
            description = data['description'].strip()
            if not description:
                return jsonify({'message': 'Audience description cannot be empty'}), 400
            audience.description = description
        
        db.session.commit()
        
        return jsonify({
            'message': 'Target audience updated successfully',
            'target_audience': audience.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to update target audience: {str(e)}'}), 500

@audience_bp.route('/<int:audience_id>', methods=['DELETE'])
def delete_audience(audience_id):
    """Delete a target audience"""
    try:
        # Get session fingerprint from request
        session_id = getattr(request, 'fingerprint', 'anonymous')
        
        audience = TargetAudience.query.filter_by(
            audience_id=audience_id,
            user_id=session_id
        ).first()
        
        if not audience:
            return jsonify({'message': 'Audience not found or access denied'}), 404
        
        # Don't allow deletion of predefined audiences
        if audience.user_id is None:
            return jsonify({'message': 'Cannot delete predefined audiences'}), 403
        
        db.session.delete(audience)
        db.session.commit()
        
        return jsonify({
            'message': 'Target audience deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to delete target audience: {str(e)}'}), 500

