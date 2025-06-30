from flask import Blueprint, request, jsonify
from src.models.user_simple import db, BusinessType

business_bp = Blueprint('business', __name__)

@business_bp.route('', methods=['GET'])
def get_business_types():
    """Get all business types (predefined + session-based custom)"""
    try:
        # Get session fingerprint from request
        session_id = getattr(request, 'fingerprint', 'anonymous')
        
        # Get predefined business types (user_id is None) and session's custom business types
        business_types = BusinessType.query.filter(
            (BusinessType.user_id == session_id) | (BusinessType.user_id == None)
        ).all()
        
        return jsonify({
            'business_types': [bt.to_dict() for bt in business_types],
            'session_id': session_id
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get business types: {str(e)}'}), 500

@business_bp.route('', methods=['POST'])
def create_business_type():
    """Create a new custom business type"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        # Get session fingerprint from request
        session_id = getattr(request, 'fingerprint', 'anonymous')
        
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        industry_category = data.get('industry_category', '').strip()
        
        if not name:
            return jsonify({'message': 'Business name is required'}), 400
        
        if not description:
            return jsonify({'message': 'Business description is required'}), 400
        
        if not industry_category:
            return jsonify({'message': 'Industry category is required'}), 400
        
        # Check if business type already exists for this session
        existing = BusinessType.query.filter_by(
            name=name, 
            user_id=session_id
        ).first()
        
        if existing:
            return jsonify({'message': 'Business type with this name already exists'}), 409
        
        # Create new business type
        business_type = BusinessType(
            name=name,
            description=description,
            industry_category=industry_category,
            user_id=session_id  # Use session fingerprint instead of user_id
        )
        
        db.session.add(business_type)
        db.session.commit()
        
        return jsonify({
            'message': 'Business type created successfully',
            'business_type': business_type.to_dict(),
            'session_id': session_id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to create business type: {str(e)}'}), 500

@business_bp.route('/<int:business_id>', methods=['PUT'])
def update_business_type(business_id):
    """Update a business type"""
    try:
        # Get session fingerprint from request
        session_id = getattr(request, 'fingerprint', 'anonymous')
        
        business_type = BusinessType.query.filter_by(
            business_type_id=business_id,
            user_id=session_id
        ).first()
        
        if not business_type:
            return jsonify({'message': 'Business type not found or access denied'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        # Update fields if provided
        if 'name' in data:
            name = data['name'].strip()
            if not name:
                return jsonify({'message': 'Business name cannot be empty'}), 400
            business_type.name = name
        
        if 'description' in data:
            description = data['description'].strip()
            if not description:
                return jsonify({'message': 'Business description cannot be empty'}), 400
            business_type.description = description
        
        if 'industry_category' in data:
            industry_category = data['industry_category'].strip()
            if not industry_category:
                return jsonify({'message': 'Industry category cannot be empty'}), 400
            business_type.industry_category = industry_category
        
        db.session.commit()
        
        return jsonify({
            'message': 'Business type updated successfully',
            'business_type': business_type.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to update business type: {str(e)}'}), 500

@business_bp.route('/<int:business_id>', methods=['DELETE'])
def delete_business_type(business_id):
    """Delete a business type"""
    try:
        # Get session fingerprint from request
        session_id = getattr(request, 'fingerprint', 'anonymous')
        
        business_type = BusinessType.query.filter_by(
            business_type_id=business_id,
            user_id=session_id
        ).first()
        
        if not business_type:
            return jsonify({'message': 'Business type not found or access denied'}), 404
        
        # Don't allow deletion of predefined business types
        if business_type.user_id is None:
            return jsonify({'message': 'Cannot delete predefined business types'}), 403
        
        db.session.delete(business_type)
        db.session.commit()
        
        return jsonify({
            'message': 'Business type deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to delete business type: {str(e)}'}), 500

