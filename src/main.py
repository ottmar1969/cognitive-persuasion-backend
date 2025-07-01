import os
import sys
from datetime import timedelta
import hashlib
import time
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS

def create_app():
    app = Flask(__name__, static_folder='../frontend/dist', static_url_path='/')
    CORS(app, origins="*")
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['OPENAI_API_KEY'] = os.environ.get('OPENAI_API_KEY', '')
    app.config['CONTACT_NAME'] = 'O. Francisca'
    app.config['CONTACT_WHATSAPP'] = '+31628073996'
    app.config['COMPANY_URL'] = 'VisitorIntel'
    
    @app.route('/api/health')
    def health():
        return jsonify({
            "status": "healthy",
            "authentication": "disabled",
            "contact": app.config['CONTACT_NAME'],
            "whatsapp": app.config['CONTACT_WHATSAPP']
        })
    
    @app.route('/api/businesses', methods=['GET', 'POST'])
    def businesses():
        if request.method == 'GET':
            return jsonify([])
        return jsonify({"message": "Business created"})
    
    @app.route('/api/audiences', methods=['GET', 'POST'])
    def audiences():
        if request.method == 'GET':
            return jsonify([])
        return jsonify({"message": "Audience created"})
    
    @app.route('/')
    def serve():
        return jsonify({"message": "Cognitive Persuasion Engine API - No Auth Version"})
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
