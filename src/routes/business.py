from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import db, User, BusinessType
from src.utils.init_data import get_predefined_business_types

business_bp = Blueprint('business', __name__)

@business_bp.route('', methods=['GET'])
@jwt_required()
def get_businesses():
    """Get all business types for the current user, including predefined ones."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        # Get user's custom business types
        user_businesses = BusinessType.query.filter_by(user_id=current_user_id).all()
        
        # Get predefined business types
        predefined_businesses = get_predefined_business_types()
        
        # Combine and format response
        all_businesses = []
        
        # Add predefined businesses
        for business in predefined_businesses:
            business_dict = business.to_dict()
            business_dict['is_predefined'] = True
            all_businesses.append(business_dict)
        
        # Add user's custom businesses
        for business in user_businesses:
            business_dict = business.to_dict()
            business_dict['is_predefined'] = False
            all_businesses.append(business_dict)
        
        return jsonify({
            'businesses': all_businesses,
            'total': len(all_businesses),
            'custom_count': len(user_businesses),
            'predefined_count': len(predefined_businesses)
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get businesses: {str(e)}'}), 500

@business_bp.route('', methods=['POST'])
@jwt_required()
def create_business():
    """Create a new custom business type for the current user."""
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
        
        # Check if user already has a business with this name
        existing_business = BusinessType.query.filter_by(
            user_id=current_user_id, 
            name=name
        ).first()
        
        if existing_business:
            return jsonify({'message': 'You already have a business type with this name'}), 409
        
        # Create new business type
        business = BusinessType(
            user_id=current_user_id,
            name=name,
            description=description,
            industry_category=industry_category,
            is_custom=True
        )
        
        db.session.add(business)
        db.session.commit()
        
        business_dict = business.to_dict()
        business_dict['is_predefined'] = False
        
        return jsonify({
            'message': 'Business type created successfully',
            'business': business_dict
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to create business: {str(e)}'}), 500

@business_bp.route('/<business_id>', methods=['GET'])
@jwt_required()
def get_business(business_id):
    """Get a specific business type."""
    try:
        current_user_id = get_jwt_identity()
        
        # Try to find the business (either user's custom or predefined)
        business = BusinessType.query.filter(
            db.or_(
                db.and_(BusinessType.business_type_id == business_id, BusinessType.user_id == current_user_id),
                db.and_(BusinessType.business_type_id == business_id, BusinessType.is_custom == False)
            )
        ).first()
        
        if not business:
            return jsonify({'message': 'Business type not found'}), 404
        
        business_dict = business.to_dict()
        business_dict['is_predefined'] = not business.is_custom
        
        return jsonify({'business': business_dict}), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get business: {str(e)}'}), 500

@business_bp.route('/<business_id>', methods=['PUT'])
@jwt_required()
def update_business(business_id):
    """Update a custom business type (only user's own custom businesses can be updated)."""
    try:
        current_user_id = get_jwt_identity()
        
        # Only allow updating user's custom business types
        business = BusinessType.query.filter_by(
            business_type_id=business_id,
            user_id=current_user_id,
            is_custom=True
        ).first()
        
        if not business:
            return jsonify({'message': 'Business type not found or cannot be modified'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        # Update fields if provided
        if 'name' in data:
            new_name = data['name'].strip()
            if not new_name:
                return jsonify({'message': 'Business name cannot be empty'}), 400
            
            # Check if user already has another business with this name
            existing_business = BusinessType.query.filter_by(
                user_id=current_user_id,
                name=new_name
            ).filter(BusinessType.business_type_id != business_id).first()
            
            if existing_business:
                return jsonify({'message': 'You already have a business type with this name'}), 409
            
            business.name = new_name
        
        if 'description' in data:
            business.description = data['description'].strip()
        
        if 'industry_category' in data:
            business.industry_category = data['industry_category'].strip()
        
        db.session.commit()
        
        business_dict = business.to_dict()
        business_dict['is_predefined'] = False
        
        return jsonify({
            'message': 'Business type updated successfully',
            'business': business_dict
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to update business: {str(e)}'}), 500

@business_bp.route('/<business_id>', methods=['DELETE'])
@jwt_required()
def delete_business(business_id):
    """Delete a custom business type (only user's own custom businesses can be deleted)."""
    try:
        current_user_id = get_jwt_identity()
        
        # Only allow deleting user's custom business types
        business = BusinessType.query.filter_by(
            business_type_id=business_id,
            user_id=current_user_id,
            is_custom=True
        ).first()
        
        if not business:
            return jsonify({'message': 'Business type not found or cannot be deleted'}), 404
        
        # Check if business is being used in any AI sessions
        if business.ai_sessions:
            return jsonify({
                'message': 'Cannot delete business type that is being used in AI sessions',
                'sessions_count': len(business.ai_sessions)
            }), 409
        
        db.session.delete(business)
        db.session.commit()
        
        return jsonify({'message': 'Business type deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to delete business: {str(e)}'}), 500

@business_bp.route('/predefined', methods=['GET'])
def get_predefined_businesses():
    """Get all predefined business types (public endpoint)."""
    try:
        predefined_businesses = get_predefined_business_types()
        
        businesses = []
        for business in predefined_businesses:
            business_dict = business.to_dict()
            business_dict['is_predefined'] = True
            businesses.append(business_dict)
        
        return jsonify({
            'businesses': businesses,
            'total': len(businesses)
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get predefined businesses: {str(e)}'}), 500

@business_bp.route('/search', methods=['GET'])
@jwt_required()
def search_businesses():
    """Search business types by name or industry category."""
    try:
        current_user_id = get_jwt_identity()
        query = request.args.get('q', '').strip()
        industry = request.args.get('industry', '').strip()
        
        if not query and not industry:
            return jsonify({'message': 'Search query or industry filter is required'}), 400
        
        # Build search query
        search_conditions = []
        
        if query:
            search_conditions.append(BusinessType.name.ilike(f'%{query}%'))
        
        if industry:
            search_conditions.append(BusinessType.industry_category.ilike(f'%{industry}%'))
        
        # Search in both user's custom businesses and predefined ones
        businesses = BusinessType.query.filter(
            db.and_(
                db.or_(*search_conditions),
                db.or_(
                    BusinessType.user_id == current_user_id,
                    BusinessType.is_custom == False
                )
            )
        ).all()
        
        results = []
        for business in businesses:
            business_dict = business.to_dict()
            business_dict['is_predefined'] = not business.is_custom
            results.append(business_dict)
        
        return jsonify({
            'businesses': results,
            'total': len(results),
            'query': query,
            'industry_filter': industry
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Search failed: {str(e)}'}), 500

