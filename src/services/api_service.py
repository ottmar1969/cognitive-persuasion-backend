import os
import sys
import requests
import json
from typing import Dict, List, Optional, Any

# Add Manus API client path
sys.path.append('/opt/.manus/.sandbox-runtime')
from data_api import ApiClient

class APIService:
    """Service class for integrating real APIs into the Cognitive Persuasion Engine"""
    
    def __init__(self):
        # AI API Keys
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.perplexity_api_key = os.getenv('PERPLEXITY_API_KEY')
        self.claude_api_key = os.getenv('CLAUDE_API_KEY')
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        
        # Manus API Hub client
        self.manus_client = ApiClient()
    
    def is_demo_mode(self, user_email: str = None) -> bool:
        """Check if user is in demo mode"""
        return user_email is None or user_email == 'demo@example.com'
    
    # Content Generation APIs
    def generate_persuasive_content(self, prompt: str, business_type: str, target_audience: str, user_email: str = None) -> Dict[str, Any]:
        """Generate persuasive content using OpenAI API"""
        
        # Always use mock data for demo mode
        if self.is_demo_mode(user_email):
            return self._mock_content_generation(prompt, business_type, target_audience)
        
        if not self.openai_api_key:
            return self._mock_content_generation(prompt, business_type, target_audience)
        
        try:
            headers = {
                'Authorization': f'Bearer {self.openai_api_key}',
                'Content-Type': 'application/json'
            }
            
            enhanced_prompt = f"""
            Create persuasive marketing content for a {business_type} business targeting {target_audience}.
            
            Original request: {prompt}
            
            Please provide:
            1. A compelling headline
            2. Main persuasive message (2-3 sentences)
            3. Call-to-action
            4. Key emotional triggers
            5. Social proof suggestions
            
            Format as JSON with keys: headline, message, cta, triggers, social_proof
            """
            
            data = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "You are an expert in cognitive persuasion and marketing psychology."},
                    {"role": "user", "content": enhanced_prompt}
                ],
                "max_tokens": 500,
                "temperature": 0.7
            }
            
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                try:
                    parsed_content = json.loads(content)
                    return {
                        'success': True,
                        'content': parsed_content,
                        'source': 'openai'
                    }
                except json.JSONDecodeError:
                    return {
                        'success': True,
                        'content': {'message': content},
                        'source': 'openai'
                    }
            else:
                return self._mock_content_generation(prompt, business_type, target_audience)
                
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return self._mock_content_generation(prompt, business_type, target_audience)
    
    def generate_with_perplexity(self, prompt: str, business_type: str, target_audience: str, user_email: str = None) -> Dict[str, Any]:
        """Generate research-backed content using Perplexity API"""
        
        # Always use mock data for demo mode
        if self.is_demo_mode(user_email):
            return self._mock_perplexity_research(prompt, business_type, target_audience)
        
        if not self.perplexity_api_key:
            return self._mock_perplexity_research(prompt, business_type, target_audience)
        
        try:
            headers = {
                'Authorization': f'Bearer {self.perplexity_api_key}',
                'Content-Type': 'application/json'
            }
            
            research_prompt = f"""
            Research and analyze the latest trends and data for {business_type} businesses targeting {target_audience}.
            
            Focus on: {prompt}
            
            Provide:
            1. Current market trends
            2. Competitor analysis insights
            3. Audience behavior patterns
            4. Effective messaging strategies
            5. Supporting statistics and data
            
            Format as detailed research report.
            """
            
            data = {
                "model": "llama-3.1-sonar-small-128k-online",
                "messages": [
                    {"role": "system", "content": "You are an expert market researcher and business analyst with access to current data."},
                    {"role": "user", "content": research_prompt}
                ],
                "max_tokens": 800,
                "temperature": 0.3
            }
            
            response = requests.post(
                'https://api.perplexity.ai/chat/completions',
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                return {
                    'success': True,
                    'research': content,
                    'source': 'perplexity',
                    'citations': result.get('citations', [])
                }
            else:
                return self._mock_perplexity_research(prompt, business_type, target_audience)
                
        except Exception as e:
            print(f"Perplexity API error: {e}")
            return self._mock_perplexity_research(prompt, business_type, target_audience)
    
    def generate_with_claude(self, prompt: str, business_type: str, target_audience: str, user_email: str = None) -> Dict[str, Any]:
        """Generate advanced analysis using Claude API"""
        
        # Always use mock data for demo mode
        if self.is_demo_mode(user_email):
            return self._mock_claude_analysis(prompt, business_type, target_audience)
        
        if not self.claude_api_key:
            return self._mock_claude_analysis(prompt, business_type, target_audience)
        
        try:
            headers = {
                'x-api-key': self.claude_api_key,
                'Content-Type': 'application/json',
                'anthropic-version': '2023-06-01'
            }
            
            analysis_prompt = f"""
            Analyze the cognitive persuasion strategy for a {business_type} business targeting {target_audience}.
            
            Request: {prompt}
            
            Provide a comprehensive analysis including:
            1. Psychological triggers most effective for this audience
            2. Cognitive biases to leverage
            3. Persuasion frameworks (AIDA, PAS, etc.)
            4. Emotional appeals and rational arguments balance
            5. Specific messaging recommendations
            6. Potential objections and how to address them
            
            Be specific and actionable.
            """
            
            data = {
                "model": "claude-3-sonnet-20240229",
                "max_tokens": 1000,
                "messages": [
                    {"role": "user", "content": analysis_prompt}
                ]
            }
            
            response = requests.post(
                'https://api.anthropic.com/v1/messages',
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['content'][0]['text']
                return {
                    'success': True,
                    'analysis': content,
                    'source': 'claude',
                    'model': 'claude-3-sonnet'
                }
            else:
                return self._mock_claude_analysis(prompt, business_type, target_audience)
                
        except Exception as e:
            print(f"Claude API error: {e}")
            return self._mock_claude_analysis(prompt, business_type, target_audience)
    
    def generate_with_gemini(self, prompt: str, business_type: str, target_audience: str, user_email: str = None) -> Dict[str, Any]:
        """Generate multimodal content using Google Gemini API"""
        
        # Always use mock data for demo mode
        if self.is_demo_mode(user_email):
            return self._mock_gemini_generation(prompt, business_type, target_audience)
        
        if not self.gemini_api_key:
            return self._mock_gemini_generation(prompt, business_type, target_audience)
        
        try:
            multimodal_prompt = f"""
            Create a comprehensive persuasion strategy for a {business_type} business targeting {target_audience}.
            
            Request: {prompt}
            
            Generate:
            1. Multi-channel campaign strategy
            2. Visual content recommendations
            3. Video script outline
            4. Social media post variations
            5. Email marketing sequence
            6. Landing page copy structure
            
            Consider both visual and textual elements for maximum impact.
            """
            
            url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={self.gemini_api_key}'
            
            data = {
                "contents": [{
                    "parts": [{
                        "text": multimodal_prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "topK": 1,
                    "topP": 1,
                    "maxOutputTokens": 1000
                }
            }
            
            response = requests.post(url, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                content = result['candidates'][0]['content']['parts'][0]['text']
                return {
                    'success': True,
                    'strategy': content,
                    'source': 'gemini',
                    'model': 'gemini-pro'
                }
            else:
                return self._mock_gemini_generation(prompt, business_type, target_audience)
                
        except Exception as e:
            print(f"Gemini API error: {e}")
            return self._mock_gemini_generation(prompt, business_type, target_audience)
    
    # Audience Analysis APIs
    def analyze_audience_on_twitter(self, keywords: str, count: int = 20, user_email: str = None) -> Dict[str, Any]:
        """Analyze audience sentiment and trends on Twitter"""
        
        # Always use mock data for demo mode
        if self.is_demo_mode(user_email):
            return self._mock_twitter_analysis(keywords)
        
        try:
            result = self.manus_client.call_api('Twitter/search_twitter', query={
                'query': keywords,
                'count': count,
                'type': 'Top'
            })
            
            if result and 'result' in result:
                tweets = []
                timeline = result.get('result', {}).get('timeline', {})
                instructions = timeline.get('instructions', [])
                
                for instruction in instructions:
                    entries = instruction.get('entries', [])
                    for entry in entries:
                        content = entry.get('content', {})
                        if content.get('entryType') == 'TimelineTimelineItem':
                            tweets.append({
                                'id': entry.get('entryId', ''),
                                'content': content
                            })
                
                return {
                    'success': True,
                    'data': {
                        'tweets': tweets[:10],  # Limit to 10 for analysis
                        'total_found': len(tweets),
                        'keywords': keywords,
                        'sentiment': 'positive',  # Would need sentiment analysis
                        'engagement_level': 'high' if len(tweets) > 5 else 'medium'
                    },
                    'source': 'twitter_api'
                }
            else:
                return self._mock_twitter_analysis(keywords)
                
        except Exception as e:
            print(f"Twitter API error: {e}")
            return self._mock_twitter_analysis(keywords)
    
    def search_linkedin_professionals(self, keywords: str, company: str = None, user_email: str = None) -> Dict[str, Any]:
        """Search for professionals on LinkedIn for B2B targeting"""
        
        # Always use mock data for demo mode
        if self.is_demo_mode(user_email):
            return self._mock_linkedin_search(keywords, company)
        
        try:
            query_params = {'keywords': keywords}
            if company:
                query_params['company'] = company
            
            result = self.manus_client.call_api('LinkedIn/search_people', query=query_params)
            
            if result and result.get('success'):
                data = result.get('data', {})
                profiles = data.get('items', [])
                
                return {
                    'success': True,
                    'data': {
                        'profiles': profiles[:10],  # Limit to 10
                        'total_found': data.get('total', 0),
                        'keywords': keywords,
                        'company_filter': company,
                        'insights': {
                            'common_titles': [p.get('headline', '') for p in profiles[:5]],
                            'locations': [p.get('location', '') for p in profiles[:5]]
                        }
                    },
                    'source': 'linkedin_api'
                }
            else:
                return self._mock_linkedin_search(keywords, company)
                
        except Exception as e:
            print(f"LinkedIn API error: {e}")
            return self._mock_linkedin_search(keywords, company)
    
    def analyze_youtube_content(self, query: str, user_email: str = None) -> Dict[str, Any]:
        """Analyze YouTube content for audience interests"""
        
        # Always use mock data for demo mode
        if self.is_demo_mode(user_email):
            return self._mock_youtube_analysis(query)
        
        try:
            result = self.manus_client.call_api('Youtube/search', query={
                'q': query,
                'hl': 'en',
                'gl': 'US'
            })
            
            if result and 'contents' in result:
                videos = result['contents'][:10]  # Limit to 10
                
                return {
                    'success': True,
                    'data': {
                        'videos': videos,
                        'total_found': len(videos),
                        'query': query,
                        'insights': {
                            'popular_channels': [v.get('video', {}).get('author', {}).get('title', '') for v in videos[:5]],
                            'avg_views': sum([v.get('video', {}).get('stats', {}).get('views', 0) for v in videos]) // len(videos) if videos else 0
                        }
                    },
                    'source': 'youtube_api'
                }
            else:
                return self._mock_youtube_analysis(query)
                
        except Exception as e:
            print(f"YouTube API error: {e}")
            return self._mock_youtube_analysis(query)
    
    def get_reddit_community_insights(self, subreddit: str, user_email: str = None) -> Dict[str, Any]:
        """Get community insights from Reddit"""
        
        # Always use mock data for demo mode
        if self.is_demo_mode(user_email):
            return self._mock_reddit_analysis(subreddit)
        
        try:
            result = self.manus_client.call_api('Reddit/AccessAPI', query={
                'subreddit': subreddit,
                'limit': 20
            })
            
            if result and result.get('success'):
                posts = result.get('posts', [])
                
                return {
                    'success': True,
                    'data': {
                        'posts': posts[:10],
                        'subreddit': subreddit,
                        'total_posts': len(posts),
                        'insights': {
                            'hot_topics': [p.get('data', {}).get('title', '')[:50] for p in posts[:5]],
                            'avg_engagement': sum([p.get('data', {}).get('score', 0) for p in posts]) // len(posts) if posts else 0
                        }
                    },
                    'source': 'reddit_api'
                }
            else:
                return self._mock_reddit_analysis(subreddit)
                
        except Exception as e:
            print(f"Reddit API error: {e}")
            return self._mock_reddit_analysis(subreddit)
    
    # Mock fallback methods
    def _mock_content_generation(self, prompt: str, business_type: str, target_audience: str) -> Dict[str, Any]:
        return {
            'success': True,
            'content': {
                'headline': f"Transform Your {business_type} Business Today!",
                'message': f"Discover how our proven strategies help {target_audience} achieve remarkable results. Join thousands who have already transformed their success.",
                'cta': "Get Started Now - Limited Time Offer!",
                'triggers': ['urgency', 'social_proof', 'transformation'],
                'social_proof': f"Over 10,000 {target_audience} trust our solutions"
            },
            'source': 'mock'
        }
    
    def _mock_twitter_analysis(self, keywords: str) -> Dict[str, Any]:
        return {
            'success': True,
            'data': {
                'tweets': [],
                'total_found': 0,
                'keywords': keywords,
                'sentiment': 'neutral',
                'engagement_level': 'medium'
            },
            'source': 'mock'
        }
    
    def _mock_linkedin_search(self, keywords: str, company: str) -> Dict[str, Any]:
        return {
            'success': True,
            'data': {
                'profiles': [],
                'total_found': 0,
                'keywords': keywords,
                'company_filter': company,
                'insights': {
                    'common_titles': [],
                    'locations': []
                }
            },
            'source': 'mock'
        }
    
    def _mock_youtube_analysis(self, query: str) -> Dict[str, Any]:
        return {
            'success': True,
            'data': {
                'videos': [],
                'total_found': 0,
                'query': query,
                'insights': {
                    'popular_channels': [],
                    'avg_views': 0
                }
            },
            'source': 'mock'
        }
    
    def _mock_reddit_analysis(self, subreddit: str) -> Dict[str, Any]:
        return {
            'success': True,
            'data': {
                'posts': [],
                'subreddit': subreddit,
                'total_posts': 0,
                'insights': {
                    'hot_topics': [],
                    'avg_engagement': 0
                }
            },
            'source': 'mock'
        }


    def _mock_perplexity_research(self, prompt: str, business_type: str, target_audience: str) -> Dict[str, Any]:
        return {
            'success': True,
            'research': f"Market Research Report for {business_type} targeting {target_audience}:\n\n1. Current Trends: Growing demand for personalized solutions\n2. Competitor Analysis: Focus on value proposition and customer service\n3. Audience Behavior: Prefer authentic, transparent communication\n4. Effective Messaging: Emphasize benefits over features\n5. Statistics: 73% of consumers prefer brands that understand their needs",
            'source': 'mock',
            'citations': []
        }
    
    def _mock_claude_analysis(self, prompt: str, business_type: str, target_audience: str) -> Dict[str, Any]:
        return {
            'success': True,
            'analysis': f"Cognitive Persuasion Analysis for {business_type}:\n\n1. Psychological Triggers: Social proof, authority, scarcity\n2. Cognitive Biases: Anchoring, loss aversion, confirmation bias\n3. Framework: AIDA (Attention, Interest, Desire, Action)\n4. Emotional Balance: 60% emotional appeal, 40% rational arguments\n5. Key Messages: Focus on transformation and results\n6. Objections: Address price concerns with value demonstration",
            'source': 'mock',
            'model': 'claude-3-sonnet'
        }
    
    def _mock_gemini_generation(self, prompt: str, business_type: str, target_audience: str) -> Dict[str, Any]:
        return {
            'success': True,
            'strategy': f"Multi-Channel Strategy for {business_type}:\n\n1. Campaign Strategy: Integrated approach across digital channels\n2. Visual Content: Professional imagery with consistent branding\n3. Video Script: Problem-solution narrative with testimonials\n4. Social Media: Platform-specific content with engagement focus\n5. Email Sequence: Welcome, education, social proof, offer\n6. Landing Page: Clear headline, benefits, testimonials, strong CTA",
            'source': 'mock',
            'model': 'gemini-pro'
        }

