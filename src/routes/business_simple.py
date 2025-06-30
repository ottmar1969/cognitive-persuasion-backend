from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user_simple import db, User, BusinessType

business_bp = Blueprint('business', __name__)

@business_bp.route('', methods=['GET'])
@jwt_required()
def get_business_types():
    """Get all business types (predefined + user's custom)"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get predefined business types (user_id is None) and user's custom business types
        business_types = BusinessType.query.filter(
            (BusinessType.user_id == current_user_id) | (BusinessType.user_id == None)
        ).all()
        
        return jsonify({
            'business_types': [bt.to_dict() for bt in business_types]
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get business types: {str(e)}'}), 500

@business_bp.route('', methods=['POST'])
@jwt_required()
def create_business_type():
    """Create a new custom business type"""
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
        industry_category = data.get('industry_category', '').strip()
        
        if not name:
            return jsonify({'message': 'Business name is required'}), 400
        
        # Check if user already has a business type with this name
        existing = BusinessType.query.filter_by(
            user_id=current_user_id,
            name=name
        ).first()
        
        if existing:
            return jsonify({'message': 'You already have a business type with this name'}), 409
        
        # Create new business type
        business_type = BusinessType(
            user_id=current_user_id,
            name=name,
            description=description,
            industry_category=industry_category,
            is_custom=True
        )
        
        db.session.add(business_type)
        db.session.commit()
        
        return jsonify({
            'message': 'Business type created successfully',
            'business_type': business_type.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to create business type: {str(e)}'}), 500

@business_bp.route('/<business_type_id>', methods=['GET'])
@jwt_required()
def get_business_type(business_type_id):
    """Get a specific business type"""
    try:
        current_user_id = get_jwt_identity()
        
        business_type = BusinessType.query.filter(
            BusinessType.business_type_id == business_type_id,
            (BusinessType.user_id == current_user_id) | (BusinessType.user_id == None)
        ).first()
        
        if not business_type:
            return jsonify({'message': 'Business type not found'}), 404
        
        return jsonify({
            'business_type': business_type.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get business type: {str(e)}'}), 500

@business_bp.route('/<business_type_id>', methods=['PUT'])
@jwt_required()
def update_business_type(business_type_id):
    """Update a custom business type"""
    try:
        current_user_id = get_jwt_identity()
        
        business_type = BusinessType.query.filter_by(
            business_type_id=business_type_id,
            user_id=current_user_id,
            is_custom=True
        ).first()
        
        if not business_type:
            return jsonify({'message': 'Business type not found or not editable'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        # Update fields
        if 'name' in data:
            name = data['name'].strip()
            if not name:
                return jsonify({'message': 'Business name cannot be empty'}), 400
            
            # Check for duplicate name
            existing = BusinessType.query.filter(
                BusinessType.user_id == current_user_id,
                BusinessType.name == name,
                BusinessType.business_type_id != business_type_id
            ).first()
            
            if existing:
                return jsonify({'message': 'You already have a business type with this name'}), 409
            
            business_type.name = name
        
        if 'description' in data:
            business_type.description = data['description'].strip()
        
        if 'industry_category' in data:
            business_type.industry_category = data['industry_category'].strip()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Business type updated successfully',
            'business_type': business_type.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to update business type: {str(e)}'}), 500

@business_bp.route('/<business_type_id>', methods=['DELETE'])
@jwt_required()
def delete_business_type(business_type_id):
    """Delete a custom business type"""
    try:
        current_user_id = get_jwt_identity()
        
        business_type = BusinessType.query.filter_by(
            business_type_id=business_type_id,
            user_id=current_user_id,
            is_custom=True
        ).first()
        
        if not business_type:
            return jsonify({'message': 'Business type not found or not deletable'}), 404
        
        db.session.delete(business_type)
        db.session.commit()
        
        return jsonify({
            'message': 'Business type deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to delete business type: {str(e)}'}), 500

