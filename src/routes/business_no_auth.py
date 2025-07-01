from flask import Blueprint, request, jsonify
from models.user_simple import db, BusinessType
import uuid
from datetime import datetime

business_bp = Blueprint('business', __name__)

@business_bp.route('', methods=['GET'])
def get_business_types():
    """Get all business types (no auth required)"""
    try:
        # Get all business types for demo purposes
        business_types = BusinessType.query.all()
        
        return jsonify({
            'business_types': [bt.to_dict() for bt in business_types]
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get business types: {str(e)}'}), 500

@business_bp.route('', methods=['POST'])
def create_business_type():
    """Create a new business type (no auth required)"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        industry_category = data.get('industry_category', '').strip()
        
        if not name:
            return jsonify({'message': 'Business name is required'}), 400
        
        # Check if business type with this name already exists
        existing = BusinessType.query.filter_by(name=name).first()
        
        if existing:
            return jsonify({'message': 'A business type with this name already exists'}), 409
        
        # Create new business type with generated ID
        business_type = BusinessType(
            business_type_id=str(uuid.uuid4()),
            user_id=None,  # No user association in no-auth mode
            name=name,
            description=description,
            industry_category=industry_category,
            is_custom=True,
            created_at=datetime.utcnow()
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
def get_business_type(business_type_id):
    """Get a specific business type (no auth required)"""
    try:
        business_type = BusinessType.query.filter_by(business_type_id=business_type_id).first()
        
        if not business_type:
            return jsonify({'message': 'Business type not found'}), 404
        
        return jsonify({
            'business_type': business_type.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get business type: {str(e)}'}), 500

@business_bp.route('/<business_type_id>', methods=['PUT'])
def update_business_type(business_type_id):
    """Update a business type (no auth required)"""
    try:
        business_type = BusinessType.query.filter_by(business_type_id=business_type_id).first()
        
        if not business_type:
            return jsonify({'message': 'Business type not found'}), 404
        
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
                BusinessType.name == name,
                BusinessType.business_type_id != business_type_id
            ).first()
            
            if existing:
                return jsonify({'message': 'A business type with this name already exists'}), 409
            
            business_type.name = name
        
        if 'description' in data:
            business_type.description = data['description'].strip()
        
        if 'industry_category' in data:
            business_type.industry_category = data['industry_category'].strip()
        
        business_type.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Business type updated successfully',
            'business_type': business_type.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to update business type: {str(e)}'}), 500

@business_bp.route('/<business_type_id>', methods=['DELETE'])
def delete_business_type(business_type_id):
    """Delete a business type (no auth required)"""
    try:
        business_type = BusinessType.query.filter_by(business_type_id=business_type_id).first()
        
        if not business_type:
            return jsonify({'message': 'Business type not found'}), 404
        
        db.session.delete(business_type)
        db.session.commit()
        
        return jsonify({
            'message': 'Business type deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to delete business type: {str(e)}'}), 500

