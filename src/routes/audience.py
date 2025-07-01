from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import db, User, TargetAudience
from utils.init_data import get_predefined_target_audiences

audience_bp = Blueprint('audience', __name__)

@audience_bp.route('', methods=['GET'])
@jwt_required()
def get_audiences():
    """Get all target audiences for the current user, including predefined ones."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        # Get user's custom target audiences
        user_audiences = TargetAudience.query.filter_by(user_id=current_user_id).all()
        
        # Get predefined target audiences
        predefined_audiences = get_predefined_target_audiences()
        
        # Combine and format response
        all_audiences = []
        
        # Add predefined audiences
        for audience in predefined_audiences:
            audience_dict = audience.to_dict()
            audience_dict['is_predefined'] = True
            all_audiences.append(audience_dict)
        
        # Add user's custom audiences
        for audience in user_audiences:
            audience_dict = audience.to_dict()
            audience_dict['is_predefined'] = False
            all_audiences.append(audience_dict)
        
        return jsonify({
            'audiences': all_audiences,
            'total': len(all_audiences),
            'custom_count': len(user_audiences),
            'predefined_count': len(predefined_audiences)
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get audiences: {str(e)}'}), 500

@audience_bp.route('', methods=['POST'])
@jwt_required()
def create_audience():
    """Create a new custom target audience for the current user."""
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
        demographics = data.get('demographics', {})
        psychographics = data.get('psychographics', {})
        
        if not name:
            return jsonify({'message': 'Audience name is required'}), 400
        
        # Check if user already has an audience with this name
        existing_audience = TargetAudience.query.filter_by(
            user_id=current_user_id, 
            name=name
        ).first()
        
        if existing_audience:
            return jsonify({'message': 'You already have a target audience with this name'}), 409
        
        # Validate demographics and psychographics are dictionaries
        if not isinstance(demographics, dict):
            demographics = {}
        if not isinstance(psychographics, dict):
            psychographics = {}
        
        # Create new target audience
        audience = TargetAudience(
            user_id=current_user_id,
            name=name,
            description=description,
            demographics=demographics,
            psychographics=psychographics,
            is_custom=True
        )
        
        db.session.add(audience)
        db.session.commit()
        
        audience_dict = audience.to_dict()
        audience_dict['is_predefined'] = False
        
        return jsonify({
            'message': 'Target audience created successfully',
            'audience': audience_dict
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to create audience: {str(e)}'}), 500

@audience_bp.route('/<audience_id>', methods=['GET'])
@jwt_required()
def get_audience(audience_id):
    """Get a specific target audience."""
    try:
        current_user_id = get_jwt_identity()
        
        # Try to find the audience (either user's custom or predefined)
        audience = TargetAudience.query.filter(
            db.or_(
                db.and_(TargetAudience.audience_id == audience_id, TargetAudience.user_id == current_user_id),
                db.and_(TargetAudience.audience_id == audience_id, TargetAudience.is_custom == False)
            )
        ).first()
        
        if not audience:
            return jsonify({'message': 'Target audience not found'}), 404
        
        audience_dict = audience.to_dict()
        audience_dict['is_predefined'] = not audience.is_custom
        
        return jsonify({'audience': audience_dict}), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get audience: {str(e)}'}), 500

@audience_bp.route('/<audience_id>', methods=['PUT'])
@jwt_required()
def update_audience(audience_id):
    """Update a custom target audience (only user's own custom audiences can be updated)."""
    try:
        current_user_id = get_jwt_identity()
        
        # Only allow updating user's custom target audiences
        audience = TargetAudience.query.filter_by(
            audience_id=audience_id,
            user_id=current_user_id,
            is_custom=True
        ).first()
        
        if not audience:
            return jsonify({'message': 'Target audience not found or cannot be modified'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        # Update fields if provided
        if 'name' in data:
            new_name = data['name'].strip()
            if not new_name:
                return jsonify({'message': 'Audience name cannot be empty'}), 400
            
            # Check if user already has another audience with this name
            existing_audience = TargetAudience.query.filter_by(
                user_id=current_user_id,
                name=new_name
            ).filter(TargetAudience.audience_id != audience_id).first()
            
            if existing_audience:
                return jsonify({'message': 'You already have a target audience with this name'}), 409
            
            audience.name = new_name
        
        if 'description' in data:
            audience.description = data['description'].strip()
        
        if 'demographics' in data:
            demographics = data['demographics']
            if isinstance(demographics, dict):
                audience.demographics = demographics
            else:
                return jsonify({'message': 'Demographics must be a valid object'}), 400
        
        if 'psychographics' in data:
            psychographics = data['psychographics']
            if isinstance(psychographics, dict):
                audience.psychographics = psychographics
            else:
                return jsonify({'message': 'Psychographics must be a valid object'}), 400
        
        db.session.commit()
        
        audience_dict = audience.to_dict()
        audience_dict['is_predefined'] = False
        
        return jsonify({
            'message': 'Target audience updated successfully',
            'audience': audience_dict
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to update audience: {str(e)}'}), 500

@audience_bp.route('/<audience_id>', methods=['DELETE'])
@jwt_required()
def delete_audience(audience_id):
    """Delete a custom target audience (only user's own custom audiences can be deleted)."""
    try:
        current_user_id = get_jwt_identity()
        
        # Only allow deleting user's custom target audiences
        audience = TargetAudience.query.filter_by(
            audience_id=audience_id,
            user_id=current_user_id,
            is_custom=True
        ).first()
        
        if not audience:
            return jsonify({'message': 'Target audience not found or cannot be deleted'}), 404
        
        # Check if audience is being used in any AI sessions
        if audience.ai_sessions:
            return jsonify({
                'message': 'Cannot delete target audience that is being used in AI sessions',
                'sessions_count': len(audience.ai_sessions)
            }), 409
        
        db.session.delete(audience)
        db.session.commit()
        
        return jsonify({'message': 'Target audience deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to delete audience: {str(e)}'}), 500

@audience_bp.route('/predefined', methods=['GET'])
def get_predefined_audiences():
    """Get all predefined target audiences (public endpoint)."""
    try:
        predefined_audiences = get_predefined_target_audiences()
        
        audiences = []
        for audience in predefined_audiences:
            audience_dict = audience.to_dict()
            audience_dict['is_predefined'] = True
            audiences.append(audience_dict)
        
        return jsonify({
            'audiences': audiences,
            'total': len(audiences)
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get predefined audiences: {str(e)}'}), 500

@audience_bp.route('/search', methods=['GET'])
@jwt_required()
def search_audiences():
    """Search target audiences by name or characteristics."""
    try:
        current_user_id = get_jwt_identity()
        query = request.args.get('q', '').strip()
        
        if not query:
            return jsonify({'message': 'Search query is required'}), 400
        
        # Search in both user's custom audiences and predefined ones
        audiences = TargetAudience.query.filter(
            db.and_(
                TargetAudience.name.ilike(f'%{query}%'),
                db.or_(
                    TargetAudience.user_id == current_user_id,
                    TargetAudience.is_custom == False
                )
            )
        ).all()
        
        results = []
        for audience in audiences:
            audience_dict = audience.to_dict()
            audience_dict['is_predefined'] = not audience.is_custom
            results.append(audience_dict)
        
        return jsonify({
            'audiences': results,
            'total': len(results),
            'query': query
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Search failed: {str(e)}'}), 500

@audience_bp.route('/manual', methods=['POST'])
@jwt_required()
def create_manual_audience():
    """Create a target audience from manual text input."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        manual_description = data.get('manual_description', '').strip()
        name = data.get('name', '').strip()
        
        if not manual_description:
            return jsonify({'message': 'Manual audience description is required'}), 400
        
        # Generate a name if not provided
        if not name:
            # Extract first few words as name
            words = manual_description.split()[:3]
            name = ' '.join(words).title()
            
            # Ensure uniqueness
            counter = 1
            base_name = name
            while TargetAudience.query.filter_by(user_id=current_user_id, name=name).first():
                name = f"{base_name} {counter}"
                counter += 1
        
        # Check if user already has an audience with this name
        existing_audience = TargetAudience.query.filter_by(
            user_id=current_user_id, 
            name=name
        ).first()
        
        if existing_audience:
            return jsonify({'message': 'You already have a target audience with this name'}), 409
        
        # Create audience with manual description
        audience = TargetAudience(
            user_id=current_user_id,
            name=name,
            description=manual_description,
            demographics={'manual_input': True},
            psychographics={'manual_description': manual_description},
            is_custom=True
        )
        
        db.session.add(audience)
        db.session.commit()
        
        audience_dict = audience.to_dict()
        audience_dict['is_predefined'] = False
        audience_dict['is_manual'] = True
        
        return jsonify({
            'message': 'Manual target audience created successfully',
            'audience': audience_dict
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to create manual audience: {str(e)}'}), 500

@audience_bp.route('/templates', methods=['GET'])
def get_audience_templates():
    """Get audience creation templates and examples."""
    try:
        templates = {
            'demographic_fields': [
                'age_range',
                'gender',
                'income_level',
                'education_level',
                'location',
                'occupation',
                'family_status',
                'lifestyle'
            ],
            'psychographic_fields': [
                'values',
                'interests',
                'concerns',
                'motivations',
                'decision_factors',
                'communication_preferences',
                'buying_behavior',
                'pain_points'
            ],
            'examples': [
                {
                    'name': 'Tech-Savvy Millennials',
                    'description': 'Young professionals who embrace technology and value convenience',
                    'demographics': {
                        'age_range': '25-40',
                        'income_level': '$50K-$100K',
                        'education_level': 'College educated',
                        'location': 'Urban areas'
                    },
                    'psychographics': {
                        'values': ['Innovation', 'Efficiency', 'Work-life balance'],
                        'concerns': ['Time management', 'Career growth', 'Financial security'],
                        'decision_factors': ['Reviews', 'Brand reputation', 'User experience']
                    }
                },
                {
                    'name': 'Budget-Conscious Families',
                    'description': 'Families with children who prioritize value and safety',
                    'demographics': {
                        'age_range': '30-50',
                        'family_status': 'Married with children',
                        'income_level': '$40K-$80K',
                        'location': 'Suburban areas'
                    },
                    'psychographics': {
                        'values': ['Family safety', 'Value for money', 'Quality'],
                        'concerns': ['Budget constraints', 'Child safety', 'Long-term value'],
                        'decision_factors': ['Price', 'Safety ratings', 'Warranty']
                    }
                }
            ]
        }
        
        return jsonify(templates), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get templates: {str(e)}'}), 500

