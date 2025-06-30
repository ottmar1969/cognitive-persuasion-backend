from flask import Blueprint, request, jsonify, current_app
import os

api_management_bp = Blueprint('api_management', __name__)

@api_management_bp.route('/status')
def get_api_status():
    """Get status of all configured APIs"""
    return jsonify({
        "apis": {
            "openai": {
                "name": "OpenAI",
                "configured": bool(current_app.config.get('OPENAI_API_KEY')),
                "description": "GPT models for text generation and completion"
            },
            "perplexity": {
                "name": "Perplexity AI", 
                "configured": bool(current_app.config.get('PERPLEXITY_API_KEY')),
                "description": "Real-time search and reasoning capabilities"
            },
            "gemini": {
                "name": "Google Gemini",
                "configured": bool(current_app.config.get('GEMINI_API_KEY')),
                "description": "Google's multimodal AI model"
            },
            "claude": {
                "name": "Anthropic Claude",
                "configured": bool(current_app.config.get('CLAUDE_API_KEY')),
                "description": "Constitutional AI for safe and helpful responses"
            }
        },
        "total_configured": sum([
            bool(current_app.config.get('OPENAI_API_KEY')),
            bool(current_app.config.get('PERPLEXITY_API_KEY')),
            bool(current_app.config.get('GEMINI_API_KEY')),
            bool(current_app.config.get('CLAUDE_API_KEY'))
        ])
    })

@api_management_bp.route('/configure', methods=['POST'])
def configure_apis():
    """Configure API keys (for development/testing only)"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        updated_apis = []
        
        # Update OpenAI API key
        if 'openai_api_key' in data:
            current_app.config['OPENAI_API_KEY'] = data['openai_api_key']
            updated_apis.append('OpenAI')
        
        # Update Perplexity API key
        if 'perplexity_api_key' in data:
            current_app.config['PERPLEXITY_API_KEY'] = data['perplexity_api_key']
            updated_apis.append('Perplexity')
        
        # Update Gemini API key
        if 'gemini_api_key' in data:
            current_app.config['GEMINI_API_KEY'] = data['gemini_api_key']
            updated_apis.append('Gemini')
        
        # Update Claude API key
        if 'claude_api_key' in data:
            current_app.config['CLAUDE_API_KEY'] = data['claude_api_key']
            updated_apis.append('Claude')
        
        return jsonify({
            'message': f'API keys updated for: {", ".join(updated_apis)}',
            'updated_apis': updated_apis
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to configure APIs: {str(e)}'}), 500

@api_management_bp.route('/test/<api_name>')
def test_api(api_name):
    """Test API connectivity (placeholder)"""
    api_configs = {
        'openai': current_app.config.get('OPENAI_API_KEY'),
        'perplexity': current_app.config.get('PERPLEXITY_API_KEY'),
        'gemini': current_app.config.get('GEMINI_API_KEY'),
        'claude': current_app.config.get('CLAUDE_API_KEY')
    }
    
    if api_name not in api_configs:
        return jsonify({'message': 'Invalid API name'}), 400
    
    api_key = api_configs[api_name]
    if not api_key:
        return jsonify({
            'api': api_name,
            'status': 'not_configured',
            'message': f'{api_name.title()} API key not configured'
        }), 400
    
    # In a real implementation, you would test the actual API connection here
    return jsonify({
        'api': api_name,
        'status': 'configured',
        'message': f'{api_name.title()} API key is configured (test connection not implemented)',
        'key_preview': f"{api_key[:8]}...{api_key[-4:]}" if len(api_key) > 12 else "***"
    })

@api_management_bp.route('/usage')
def get_api_usage():
    """Get API usage statistics (placeholder)"""
    return jsonify({
        "usage_stats": {
            "openai": {
                "requests_today": 0,
                "tokens_used": 0,
                "cost_estimate": "$0.00"
            },
            "perplexity": {
                "requests_today": 0,
                "searches_performed": 0,
                "cost_estimate": "$0.00"
            },
            "gemini": {
                "requests_today": 0,
                "tokens_used": 0,
                "cost_estimate": "$0.00"
            },
            "claude": {
                "requests_today": 0,
                "tokens_used": 0,
                "cost_estimate": "$0.00"
            }
        },
        "total_cost_today": "$0.00",
        "note": "Usage tracking not yet implemented"
    })

@api_management_bp.route('/models')
def get_available_models():
    """Get available models for each API"""
    return jsonify({
        "models": {
            "openai": [
                {"id": "gpt-4", "name": "GPT-4", "description": "Most capable model"},
                {"id": "gpt-4-turbo", "name": "GPT-4 Turbo", "description": "Faster and cheaper GPT-4"},
                {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "description": "Fast and efficient"}
            ],
            "perplexity": [
                {"id": "llama-3.1-sonar-small-128k-online", "name": "Sonar Small", "description": "Fast online search"},
                {"id": "llama-3.1-sonar-large-128k-online", "name": "Sonar Large", "description": "Comprehensive online search"}
            ],
            "gemini": [
                {"id": "gemini-pro", "name": "Gemini Pro", "description": "Google's most capable model"},
                {"id": "gemini-pro-vision", "name": "Gemini Pro Vision", "description": "Multimodal capabilities"}
            ],
            "claude": [
                {"id": "claude-3-opus", "name": "Claude 3 Opus", "description": "Most powerful Claude model"},
                {"id": "claude-3-sonnet", "name": "Claude 3 Sonnet", "description": "Balanced performance"},
                {"id": "claude-3-haiku", "name": "Claude 3 Haiku", "description": "Fast and efficient"}
            ]
        }
    })

