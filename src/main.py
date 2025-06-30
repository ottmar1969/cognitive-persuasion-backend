import os
import sys
from datetime import timedelta
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

from src.models.user_simple import db
from src.routes.auth_simple import auth_bp
from src.routes.business_simple import business_bp
from src.routes.audience_simple import audience_bp
from src.routes.payment_simple import payment_bp

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Use in-memory database for deployment simplicity
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///:memory:')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-change-in-production')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
    
    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)
    
    # Enhanced CORS configuration
    CORS(app, 
         origins=["*"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         allow_headers=["Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
         supports_credentials=True)
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return jsonify({"status": "healthy", "message": "Cognitive Persuasion Engine API is running"})
    
    # Root endpoint
    @app.route('/')
    def root():
        return jsonify({
            "message": "Cognitive Persuasion Engine API",
            "version": "1.0.0",
            "status": "running",
            "endpoints": {
                "auth": "/api/auth",
                "businesses": "/api/businesses", 
                "audiences": "/api/audiences",
                "payments": "/api/payments",
                "health": "/api/health"
            }
        })
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(business_bp, url_prefix='/api/businesses')
    app.register_blueprint(audience_bp, url_prefix='/api/audiences')
    app.register_blueprint(payment_bp, url_prefix='/api/payments')
    
    # Create tables
    with app.app_context():
        db.create_all()
        # Initialize sample data
        from src.utils.init_data_simple import init_sample_data
        init_sample_data()
    
    return app

# Create the app
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

