import os
import sys
from datetime import timedelta
import hashlib
import time
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS

# Create the Flask app instance directly at the top level
app = Flask(__name__)
CORS(app, origins='*')

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

# Missing endpoints that frontend expects
@app.route('/api/payments/balance', methods=['GET'])
def payments_balance():
    return jsonify({
        "balance": 100,
        "currency": "credits",
        "status": "active"
    })

@app.route('/api/session', methods=['GET'])
def session_info():
    return jsonify({
        "authenticated": False,
        "user": None,
        "session_id": "no-auth-session",
        "fingerprint": "browser-fingerprint"
    })

# Additional endpoints for completeness
@app.route('/api/contact', methods=['GET'])
def contact_info():
    return jsonify({
        "name": app.config['CONTACT_NAME'],
        "whatsapp": app.config['CONTACT_WHATSAPP'],
        "company": app.config['COMPANY_URL']
    })

@app.route('/api/legal/terms', methods=['GET'])
def legal_terms():
    return jsonify({
        "title": "Terms of Service",
        "content": "Terms of service for VisitorIntel Cognitive Persuasion Engine."
    })

@app.route('/api/legal/privacy', methods=['GET'])
def legal_privacy():
    return jsonify({
        "title": "Privacy Policy",
        "content": "Privacy policy for VisitorIntel Cognitive Persuasion Engine."
    })

@app.route('/api/legal/gdpr', methods=['GET'])
def legal_gdpr():
    return jsonify({
        "title": "GDPR Compliance",
        "content": "GDPR compliance information for VisitorIntel."
    })

@app.route('/api/legal/cookies', methods=['GET'])
def legal_cookies():
    return jsonify({
        "title": "Cookie Policy",
        "content": "Cookie policy for VisitorIntel Cognitive Persuasion Engine."
    })

@app.route('/')
def serve():
    return jsonify({"message": "Cognitive Persuasion Engine API - No Auth Version"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

