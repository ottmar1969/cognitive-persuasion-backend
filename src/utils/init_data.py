from src.models.user import db, BusinessType, TargetAudience, PREDEFINED_BUSINESS_TYPES, PREDEFINED_TARGET_AUDIENCES

def initialize_predefined_data():
    """Initialize predefined business types and target audiences if they don't exist."""
    
    # Check if we already have predefined data
    existing_business_types = BusinessType.query.filter_by(is_custom=False).count()
    existing_audiences = TargetAudience.query.filter_by(is_custom=False).count()
    
    if existing_business_types == 0:
        # Add predefined business types
        for business_data in PREDEFINED_BUSINESS_TYPES:
            business_type = BusinessType(
                user_id=None,  # System-wide predefined types
                name=business_data['name'],
                description=business_data['description'],
                industry_category=business_data['industry_category'],
                is_custom=False
            )
            db.session.add(business_type)
        
        print(f"Added {len(PREDEFINED_BUSINESS_TYPES)} predefined business types")
    
    if existing_audiences == 0:
        # Add predefined target audiences
        for audience_data in PREDEFINED_TARGET_AUDIENCES:
            target_audience = TargetAudience(
                user_id=None,  # System-wide predefined audiences
                name=audience_data['name'],
                description=audience_data['description'],
                demographics=audience_data['demographics'],
                psychographics=audience_data['psychographics'],
                is_custom=False
            )
            db.session.add(target_audience)
        
        print(f"Added {len(PREDEFINED_TARGET_AUDIENCES)} predefined target audiences")
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error initializing predefined data: {e}")

def get_predefined_business_types():
    """Get all predefined business types."""
    return BusinessType.query.filter_by(is_custom=False).all()

def get_predefined_target_audiences():
    """Get all predefined target audiences."""
    return TargetAudience.query.filter_by(is_custom=False).all()

