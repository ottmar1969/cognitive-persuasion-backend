import os
import sys
from datetime import timedelta
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

from src.models.user_simple import db
from src.routes.auth_simple import auth_bp
from src.routes.business_simple import business_bp
from src.routes.audience_simple import audience_bp
from src.routes.payment_simple import payment_bp
from src.routes.ai_session_enhanced import ai_session_bp

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///src/database/app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-change-in-production')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
    
    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)
    
    # Enable CORS for all routes
    CORS(app, origins="*", allow_headers=["Content-Type", "Authorization"])
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(business_bp, url_prefix='/api/businesses')
    app.register_blueprint(audience_bp, url_prefix='/api/audiences')
    app.register_blueprint(payment_bp, url_prefix='/api/payments')
    app.register_blueprint(ai_session_bp, url_prefix='/api/ai')
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Initialize predefined business types and audiences
        from src.utils.init_data_simple import initialize_predefined_data
        initialize_predefined_data()
    
    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return {'message': 'Token has expired'}, 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return {'message': 'Invalid token'}, 401
    
    @jwt.unauthorized_loader
    def unauthorized_callback(error):
        return {'message': 'Authorization required'}, 401
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'message': 'Cognitive Persuasion Engine API is running'}
    
    # API info endpoint
    @app.route('/api')
    def api_info():
        return {
            'name': 'Cognitive Persuasion Engine API',
            'version': '1.0.0',
            'status': 'operational'
        }
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5003, debug=True)

