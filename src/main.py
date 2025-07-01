import os
import sys
from datetime import timedelta
import hashlib
import time
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

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
    CORS(app, origins='*')

    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///cognitive_persuasion.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-string')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
    
    # API Configuration
    app.config['OPENAI_API_KEY'] = os.environ.get('OPENAI_API_KEY', '')
    app.config['ANTHROPIC_API_KEY'] = os.environ.get('ANTHROPIC_API_KEY', '')
    app.config['GOOGLE_API_KEY'] = os.environ.get('GOOGLE_API_KEY', '')
    app.config['PERPLEXITY_API_KEY'] = os.environ.get('PERPLEXITY_API_KEY', '')
    
    # Contact Configuration
    app.config['CONTACT_NAME'] = 'O. Francisca'
    app.config['CONTACT_WHATSAPP'] = '+31628073996'
    app.config['COMPANY_URL'] = 'VisitorIntel'

    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)

    # Root endpoint - serve frontend
    @app.route('/')
    def root():
        return send_from_directory('static', 'index.html')
    
    # Serve static files
    @app.route('/<path:path>')
    def serve_static(path):
        try:
            return send_from_directory('static', path)
        except:
            # If file not found, serve index.html for SPA routing
            return send_from_directory('static', 'index.html')
    
    # API root endpoint
    @app.route('/api')
    def api_root():
        return jsonify({
            "message": "Cognitive Persuasion Engine API",
            "version": "1.0.0",
            "status": "running",
            "endpoints": {
                "auth": "/api/auth",
                "businesses": "/api/businesses", 
                "audiences": "/api/audiences",
                "payments": "/api/payments",
                "ai-conversations": "/api/ai-conversations",
                "ai-search": "/api/ai-search",
                "health": "/api/health"
            }
        })
    
    # Simple audiences endpoint (temporary fix)
    @app.route('/api/audiences', methods=['GET', 'POST'])
    def audiences():
        if request.method == 'GET':
            return jsonify([])
        return jsonify({"message": "Audience created"})
    
    # Health check endpoint
    @app.route('/api/health')
    def health():
        return jsonify({
            "status": "healthy",
            "authentication": "disabled",
            "contact": app.config['CONTACT_NAME'],
            "whatsapp": app.config['CONTACT_WHATSAPP']
        })
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(business_bp, url_prefix='/api/businesses')
    app.register_blueprint(payment_bp, url_prefix='/api/payments')
    app.register_blueprint(ai_conversations_bp, url_prefix='/api/ai-conversations')
    app.register_blueprint(ai_search_bp)
    
    # Create tables
    with app.app_context():
        db.create_all()
        # Initialize sample data
        try:
            from utils.init_data_simple import initialize_predefined_data
            initialize_predefined_data()
        except Exception as e:
            print(f"Warning: Could not initialize predefined data: {e}")
    
    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

