from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from src.services.api_service import APIService

api_bp = Blueprint('api', __name__)
api_service = APIService()

@api_bp.route('/generate-content', methods=['POST'])
@jwt_required()
def generate_content():
    """Generate persuasive content using AI APIs"""
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        prompt = data.get('prompt', '')
        business_type = data.get('business_type', 'general')
        target_audience = data.get('target_audience', 'consumers')
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        result = api_service.generate_persuasive_content(prompt, business_type, target_audience, current_user)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': 'Content generated successfully',
            'demo_mode': api_service.is_demo_mode(current_user)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/analyze-audience/twitter', methods=['POST'])
@jwt_required()
def analyze_twitter_audience():
    """Analyze audience on Twitter"""
    try:
        data = request.get_json()
        keywords = data.get('keywords', '')
        count = data.get('count', 20)
        
        if not keywords:
            return jsonify({'error': 'Keywords are required'}), 400
        
        result = api_service.analyze_audience_on_twitter(keywords, count)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': 'Twitter audience analysis completed'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/analyze-audience/linkedin', methods=['POST'])
@jwt_required()
def analyze_linkedin_audience():
    """Search professionals on LinkedIn"""
    try:
        data = request.get_json()
        keywords = data.get('keywords', '')
        company = data.get('company')
        
        if not keywords:
            return jsonify({'error': 'Keywords are required'}), 400
        
        result = api_service.search_linkedin_professionals(keywords, company)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': 'LinkedIn audience analysis completed'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/analyze-audience/youtube', methods=['POST'])
@jwt_required()
def analyze_youtube_audience():
    """Analyze YouTube content for audience insights"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        result = api_service.analyze_youtube_content(query)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': 'YouTube audience analysis completed'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/analyze-audience/reddit', methods=['POST'])
@jwt_required()
def analyze_reddit_audience():
    """Get community insights from Reddit"""
    try:
        data = request.get_json()
        subreddit = data.get('subreddit', '')
        
        if not subreddit:
            return jsonify({'error': 'Subreddit is required'}), 400
        
        result = api_service.get_reddit_community_insights(subreddit)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': 'Reddit community analysis completed'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/audience-research', methods=['POST'])
@jwt_required()
def comprehensive_audience_research():
    """Perform comprehensive audience research across multiple platforms"""
    try:
        data = request.get_json()
        keywords = data.get('keywords', '')
        platforms = data.get('platforms', ['twitter', 'linkedin'])
        
        if not keywords:
            return jsonify({'error': 'Keywords are required'}), 400
        
        results = {}
        
        if 'twitter' in platforms:
            results['twitter'] = api_service.analyze_audience_on_twitter(keywords)
        
        if 'linkedin' in platforms:
            results['linkedin'] = api_service.search_linkedin_professionals(keywords)
        
        if 'youtube' in platforms:
            results['youtube'] = api_service.analyze_youtube_content(keywords)
        
        if 'reddit' in platforms and data.get('subreddit'):
            results['reddit'] = api_service.get_reddit_community_insights(data.get('subreddit'))
        
        # Compile insights
        insights = {
            'total_platforms': len(results),
            'keywords_analyzed': keywords,
            'summary': 'Comprehensive audience research completed across multiple platforms'
        }
        
        return jsonify({
            'success': True,
            'data': {
                'results': results,
                'insights': insights
            },
            'message': 'Comprehensive audience research completed'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/api-status', methods=['GET'])
def api_status():
    """Check the status of integrated APIs"""
    try:
        status = {
            'openai': bool(api_service.openai_api_key),
            'google': bool(api_service.google_api_key),
            'manus_hub': True,  # Always available
            'twitter': True,
            'linkedin': True,
            'youtube': True,
            'reddit': True
        }
        
        return jsonify({
            'success': True,
            'data': status,
            'message': 'API status retrieved successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/research', methods=['POST'])
@jwt_required()
def research_with_perplexity():
    """Generate research-backed content using Perplexity API"""
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        prompt = data.get('prompt', '')
        business_type = data.get('business_type', 'general')
        target_audience = data.get('target_audience', 'consumers')
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        result = api_service.generate_with_perplexity(prompt, business_type, target_audience, current_user)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': 'Research completed successfully',
            'demo_mode': api_service.is_demo_mode(current_user)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/analyze', methods=['POST'])
@jwt_required()
def analyze_with_claude():
    """Generate advanced analysis using Claude API"""
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        prompt = data.get('prompt', '')
        business_type = data.get('business_type', 'general')
        target_audience = data.get('target_audience', 'consumers')
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        result = api_service.generate_with_claude(prompt, business_type, target_audience, current_user)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': 'Analysis completed successfully',
            'demo_mode': api_service.is_demo_mode(current_user)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/strategy', methods=['POST'])
@jwt_required()
def generate_strategy_with_gemini():
    """Generate comprehensive strategy using Gemini API"""
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        prompt = data.get('prompt', '')
        business_type = data.get('business_type', 'general')
        target_audience = data.get('target_audience', 'consumers')
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        result = api_service.generate_with_gemini(prompt, business_type, target_audience, current_user)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': 'Strategy generated successfully',
            'demo_mode': api_service.is_demo_mode(current_user)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/comprehensive', methods=['POST'])
@jwt_required()
def comprehensive_ai_analysis():
    """Run comprehensive analysis using all AI APIs"""
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        prompt = data.get('prompt', '')
        business_type = data.get('business_type', 'general')
        target_audience = data.get('target_audience', 'consumers')
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        # Run all AI analyses
        results = {
            'openai': api_service.generate_persuasive_content(prompt, business_type, target_audience, current_user),
            'perplexity': api_service.generate_with_perplexity(prompt, business_type, target_audience, current_user),
            'claude': api_service.generate_with_claude(prompt, business_type, target_audience, current_user),
            'gemini': api_service.generate_with_gemini(prompt, business_type, target_audience, current_user)
        }
        
        return jsonify({
            'success': True,
            'data': results,
            'message': 'Comprehensive AI analysis completed',
            'demo_mode': api_service.is_demo_mode(current_user)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

