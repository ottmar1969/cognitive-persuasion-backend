from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user_simple import db, User, TargetAudience

audience_bp = Blueprint('audience', __name__)

@audience_bp.route('', methods=['GET'])
@jwt_required()
def get_target_audiences():
    """Get all target audiences (predefined + user's custom)"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get predefined audiences (user_id is None) and user's custom audiences
        audiences = TargetAudience.query.filter(
            (TargetAudience.user_id == current_user_id) | (TargetAudience.user_id == None)
        ).all()
        
        return jsonify({
            'target_audiences': [audience.to_dict() for audience in audiences]
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get target audiences: {str(e)}'}), 500

@audience_bp.route('/manual', methods=['POST'])
@jwt_required()
def create_manual_audience():
    """Create a new manual target audience"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        name = data.get('name', '').strip()
        manual_description = data.get('manual_description', '').strip()
        
        if not manual_description:
            return jsonify({'message': 'Manual description is required'}), 400
        
        # If no name provided, generate one from description
        if not name:
            # Take first few words of description as name
            words = manual_description.split()[:3]
            name = ' '.join(words).title()
        
        # Check if user already has an audience with this name
        existing = TargetAudience.query.filter_by(
            user_id=current_user_id,
            name=name
        ).first()
        
        if existing:
            return jsonify({'message': 'You already have a target audience with this name'}), 409
        
        # Create new target audience
        audience = TargetAudience(
            user_id=current_user_id,
            name=name,
            description=manual_description,  # Store in both fields for compatibility
            manual_description=manual_description,
            is_custom=True
        )
        
        db.session.add(audience)
        db.session.commit()
        
        return jsonify({
            'message': 'Target audience created successfully',
            'target_audience': audience.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to create target audience: {str(e)}'}), 500

@audience_bp.route('', methods=['POST'])
@jwt_required()
def create_structured_audience():
    """Create a new structured target audience"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        
        if not name or not description:
            return jsonify({'message': 'Name and description are required'}), 400
        
        # Check if user already has an audience with this name
        existing = TargetAudience.query.filter_by(
            user_id=current_user_id,
            name=name
        ).first()
        
        if existing:
            return jsonify({'message': 'You already have a target audience with this name'}), 409
        
        # Create new target audience
        audience = TargetAudience(
            user_id=current_user_id,
            name=name,
            description=description,
            is_custom=True
        )
        
        db.session.add(audience)
        db.session.commit()
        
        return jsonify({
            'message': 'Target audience created successfully',
            'target_audience': audience.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to create target audience: {str(e)}'}), 500

@audience_bp.route('/<audience_id>', methods=['GET'])
@jwt_required()
def get_target_audience(audience_id):
    """Get a specific target audience"""
    try:
        current_user_id = get_jwt_identity()
        
        audience = TargetAudience.query.filter(
            TargetAudience.audience_id == audience_id,
            (TargetAudience.user_id == current_user_id) | (TargetAudience.user_id == None)
        ).first()
        
        if not audience:
            return jsonify({'message': 'Target audience not found'}), 404
        
        return jsonify({
            'target_audience': audience.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get target audience: {str(e)}'}), 500

@audience_bp.route('/<audience_id>', methods=['PUT'])
@jwt_required()
def update_target_audience(audience_id):
    """Update a custom target audience"""
    try:
        current_user_id = get_jwt_identity()
        
        audience = TargetAudience.query.filter_by(
            audience_id=audience_id,
            user_id=current_user_id,
            is_custom=True
        ).first()
        
        if not audience:
            return jsonify({'message': 'Target audience not found or not editable'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        # Update fields
        if 'name' in data:
            name = data['name'].strip()
            if not name:
                return jsonify({'message': 'Audience name cannot be empty'}), 400
            
            # Check for duplicate name
            existing = TargetAudience.query.filter(
                TargetAudience.user_id == current_user_id,
                TargetAudience.name == name,
                TargetAudience.audience_id != audience_id
            ).first()
            
            if existing:
                return jsonify({'message': 'You already have a target audience with this name'}), 409
            
            audience.name = name
        
        if 'description' in data:
            audience.description = data['description'].strip()
        
        if 'manual_description' in data:
            audience.manual_description = data['manual_description'].strip()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Target audience updated successfully',
            'target_audience': audience.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to update target audience: {str(e)}'}), 500

@audience_bp.route('/<audience_id>', methods=['DELETE'])
@jwt_required()
def delete_target_audience(audience_id):
    """Delete a custom target audience"""
    try:
        current_user_id = get_jwt_identity()
        
        audience = TargetAudience.query.filter_by(
            audience_id=audience_id,
            user_id=current_user_id,
            is_custom=True
        ).first()
        
        if not audience:
            return jsonify({'message': 'Target audience not found or not deletable'}), 404
        
        db.session.delete(audience)
        db.session.commit()
        
        return jsonify({
            'message': 'Target audience deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to delete target audience: {str(e)}'}), 500

