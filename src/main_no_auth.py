import os
import sys
from datetime import timedelta
import hashlib
import time
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.models.user_simple import db
from src.routes.business_no_auth import business_bp
from src.routes.audience_no_auth import audience_bp
from src.routes.payment_simple import payment_bp
from src.routes.legal import legal_bp
from src.routes.api_management import api_management_bp

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Use persistent SQLite database for deployment
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///cognitive_persuasion.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # API Keys Configuration
    app.config['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY', '')
    app.config['PERPLEXITY_API_KEY'] = os.getenv('PERPLEXITY_API_KEY', '')
    app.config['GEMINI_API_KEY'] = os.getenv('GEMINI_API_KEY', '')
    app.config['CLAUDE_API_KEY'] = os.getenv('CLAUDE_API_KEY', '')
    
    # Contact Information
    app.config['CONTACT_NAME'] = 'O. Francisca'
    app.config['CONTACT_WHATSAPP'] = '+31628073996'
    app.config['COMPANY_URL'] = 'VisitorIntel'
    
    # Initialize extensions
    db.init_app(app)
    
    # Enhanced CORS configuration
    CORS(app, 
         origins=["*"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         allow_headers=["Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
         supports_credentials=True)
    
    # Security and tracking middleware
    @app.before_request
    def track_request():
        # Get IP address
        ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        if ip_address and ',' in ip_address:
            ip_address = ip_address.split(',')[0].strip()
        
        # Generate fingerprint from headers
        user_agent = request.headers.get('User-Agent', '')
        accept_language = request.headers.get('Accept-Language', '')
        accept_encoding = request.headers.get('Accept-Encoding', '')
        
        fingerprint_data = f"{user_agent}|{accept_language}|{accept_encoding}|{ip_address}"
        fingerprint = hashlib.sha256(fingerprint_data.encode()).hexdigest()[:16]
        
        # Store in request context
        request.ip_address = ip_address
        request.fingerprint = fingerprint
        request.timestamp = int(time.time())
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return jsonify({
            "status": "healthy", 
            "message": "Cognitive Persuasion Engine API is running",
            "authentication": "disabled",
            "security": "ip_and_fingerprint_tracking"
        })
    
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
            "version": "2.0.0",
            "status": "running",
            "authentication": "disabled",
            "security": "ip_and_fingerprint_tracking",
            "endpoints": {
                "businesses": "/api/businesses", 
                "audiences": "/api/audiences",
                "payments": "/api/payments",
                "contact": "/api/contact",
                "legal": "/api/legal",
                "apis": "/api/apis",
                "session": "/api/session",
                "health": "/api/health"
            }
        })
    
    # Contact information endpoint
    @app.route('/api/contact')
    def get_contact():
        return jsonify({
            "name": app.config['CONTACT_NAME'],
            "whatsapp": app.config['CONTACT_WHATSAPP'],
            "company": app.config['COMPANY_URL'],
            "whatsapp_url": f"https://wa.me/{app.config['CONTACT_WHATSAPP'].replace('+', '')}"
        })
    
    # Legal pages endpoint
    @app.route('/api/legal')
    def get_legal_info():
        return jsonify({
            "pages": [
                {"name": "Terms of Service", "slug": "terms"},
                {"name": "Privacy Policy", "slug": "privacy"},
                {"name": "GDPR Compliance", "slug": "gdpr"},
                {"name": "Cookie Policy", "slug": "cookies"},
                {"name": "Legal Information", "slug": "legal"}
            ]
        })
    
    # API Keys status endpoint (without exposing actual keys)
    @app.route('/api/config')
    def get_api_config():
        return jsonify({
            "apis": {
                "openai": {"configured": bool(app.config['OPENAI_API_KEY'])},
                "perplexity": {"configured": bool(app.config['PERPLEXITY_API_KEY'])},
                "gemini": {"configured": bool(app.config['GEMINI_API_KEY'])},
                "claude": {"configured": bool(app.config['CLAUDE_API_KEY'])}
            }
        })
    
    # Session tracking endpoint
    @app.route('/api/session')
    def get_session_info():
        return jsonify({
            "ip_address": request.ip_address,
            "fingerprint": request.fingerprint,
            "timestamp": request.timestamp,
            "user_agent": request.headers.get('User-Agent', ''),
            "session_id": f"{request.fingerprint}_{request.timestamp}"
        })
    
    # Register blueprints (without auth requirements)
    app.register_blueprint(business_bp, url_prefix='/api/businesses')
    app.register_blueprint(audience_bp, url_prefix='/api/audiences')
    app.register_blueprint(payment_bp, url_prefix='/api/payments')
    app.register_blueprint(legal_bp, url_prefix='/api/legal')
    app.register_blueprint(api_management_bp, url_prefix='/api/apis')
    
    # Create tables
    with app.app_context():
        db.create_all()
        # Initialize sample data
        try:
            from src.utils.init_data_simple import initialize_predefined_data
            initialize_predefined_data()
        except Exception as e:
            print(f"Warning: Could not initialize predefined data: {e}")
    
    return app

# Create the app
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)

