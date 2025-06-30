from src.models.user_simple import db, BusinessType, TargetAudience

def initialize_predefined_data():
    """Initialize predefined business types and target audiences"""
    try:
        # Check if predefined data already exists
        existing_business_types = BusinessType.query.filter_by(user_id=None).count()
        existing_audiences = TargetAudience.query.filter_by(user_id=None).count()
        
        if existing_business_types > 0 and existing_audiences > 0:
            print(f"Predefined data already exists: {existing_business_types} business types, {existing_audiences} audiences")
            return
        
        # Predefined business types
        predefined_business_types = [
            {
                'name': 'Roofing Services',
                'description': 'Residential and commercial roofing installation, repair, and maintenance services',
                'industry_category': 'Construction & Home Services'
            },
            {
                'name': 'Digital Marketing Agency',
                'description': 'Full-service digital marketing including SEO, PPC, social media, and content marketing',
                'industry_category': 'Marketing & Advertising'
            },
            {
                'name': 'Software as a Service (SaaS)',
                'description': 'Cloud-based software solutions for business productivity and automation',
                'industry_category': 'Technology'
            },
            {
                'name': 'E-commerce Store',
                'description': 'Online retail business selling products directly to consumers',
                'industry_category': 'Retail & E-commerce'
            },
            {
                'name': 'Consulting Services',
                'description': 'Professional consulting services for business strategy and operations',
                'industry_category': 'Professional Services'
            }
        ]
        
        # Predefined target audiences
        predefined_audiences = [
            {
                'name': 'Homeowners',
                'description': 'Residential property owners aged 25-65 interested in home improvement and maintenance'
            },
            {
                'name': 'Small Business Owners',
                'description': 'Entrepreneurs and business owners with 1-50 employees looking to grow their business'
            },
            {
                'name': 'Tech Professionals',
                'description': 'IT professionals, developers, and tech-savvy individuals interested in productivity tools'
            },
            {
                'name': 'Online Shoppers',
                'description': 'Consumers who regularly purchase products online and value convenience and quality'
            }
        ]
        
        # Add business types if they don't exist
        if existing_business_types == 0:
            for bt_data in predefined_business_types:
                business_type = BusinessType(
                    user_id=None,  # Predefined types have no user_id
                    name=bt_data['name'],
                    description=bt_data['description'],
                    industry_category=bt_data['industry_category'],
                    is_custom=False
                )
                db.session.add(business_type)
            
            print(f"Added {len(predefined_business_types)} predefined business types")
        
        # Add target audiences if they don't exist
        if existing_audiences == 0:
            for audience_data in predefined_audiences:
                audience = TargetAudience(
                    user_id=None,  # Predefined audiences have no user_id
                    name=audience_data['name'],
                    description=audience_data['description'],
                    is_custom=False
                )
                db.session.add(audience)
            
            print(f"Added {len(predefined_audiences)} predefined target audiences")
        
        db.session.commit()
        print("Predefined data initialization completed successfully")
        
    except Exception as e:
        db.session.rollback()
        print(f"Error initializing predefined data: {e}")
        # Don't raise the exception to prevent app startup failure

