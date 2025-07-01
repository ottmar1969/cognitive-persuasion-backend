import os
import sys
from datetime import timedelta
import hashlib
import time
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

# Import with correct relative paths (no src. prefix)
from models.user_simple import db
from routes.auth_simple import auth_bp
from routes.business_no_auth import business_bp
from routes.payment_simple import payment_bp
from routes.ai_conversations import ai_conversations_bp
from routes.ai_search_optimization import ai_search_bp

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Use persistent SQLite database for deployment
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///cognitive_persuasion.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_timeout': 20,
        'pool_recycle': -1,
        'pool_pre_ping': True
    }
    
    # OpenAI Configuration
    app.config['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY', '')
    
    # Contact Configuration
    app.config['CONTACT_NAME'] = 'O. Francisca'
    app.config['CONTACT_WHATSAPP'] = '+31628073996'
    app.config['COMPANY_URL'] = 'VisitorIntel'
    
    # Initialize extensions
    db.init_app(app)
    CORS(app, origins='*')
    
    # Create tables
    with app.app_context():
        db.create_all()
        
        # Add default business types if they don't exist
        from models.user_simple import BusinessType
        if BusinessType.query.count() == 0:
            default_businesses = [
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
            
            for biz in default_businesses:
                business_type = BusinessType(
                    name=biz['name'],
                    description=biz['description'],
                    industry_category=biz['industry_category'],
                    is_custom=False
                )
                db.session.add(business_type)
            
            db.session.commit()
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(business_bp, url_prefix='/api')
    app.register_blueprint(payment_bp, url_prefix='/api/payments')
    app.register_blueprint(ai_conversations_bp, url_prefix='/api/ai-conversations')
    app.register_blueprint(ai_search_bp, url_prefix='/api/ai-search')
    
    # Health check endpoint
    @app.route('/api/health')
    def health():
        return jsonify({
            "status": "healthy",
            "authentication": "disabled",
            "contact": app.config['CONTACT_NAME'],
            "whatsapp": app.config['CONTACT_WHATSAPP']
        })
    
    # Simple audiences endpoint (no auth required)
    @app.route('/api/audiences', methods=['GET', 'POST'])
    def audiences():
        if request.method == 'GET':
            return jsonify([])
        return jsonify({"message": "Audience created"})
    
    # Root endpoint
    @app.route('/')
    def serve():
        return jsonify({"message": "Cognitive Persuasion Engine API - No Auth Version"})
    
    return app

# Create the app
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

