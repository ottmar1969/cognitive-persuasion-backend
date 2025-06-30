import os
import requests
import json
import time
from typing import Dict, List, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedMultiAIService:
    """
    Enhanced Multi-AI service with OpenAI, Gemini, Claude, and Perplexity
    for the most diverse and powerful AI conversation system.
    """
    
    def __init__(self):
        # API Keys (should be set in environment variables)
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.gemini_api_key = os.getenv('GEMINI_API_KEY') 
        self.claude_api_key = os.getenv('CLAUDE_API_KEY')
        self.perplexity_api_key = os.getenv('PERPLEXITY_API_KEY')
        
        # API Endpoints
        self.openai_url = "https://api.openai.com/v1/chat/completions"
        self.gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={self.gemini_api_key}"
        self.claude_url = "https://api.anthropic.com/v1/messages"
        self.perplexity_url = "https://api.perplexity.ai/chat/completions"
        
        # Enhanced agent configurations with optimal provider assignment
        self.agents = {
            'logic': {
                'name': 'Logic Agent',
                'provider': 'OpenAI GPT-4',
                'model': 'gpt-4-turbo-preview',
                'personality': 'analytical, data-driven, logical reasoning',
                'focus': 'facts, statistics, logical arguments, ROI analysis',
                'cost_per_call': 0.012
            },
            'emotion': {
                'name': 'Emotion Agent',
                'provider': 'Claude (Anthropic)',
                'model': 'claude-3-sonnet-20240229',
                'personality': 'empathetic, emotionally intelligent, nuanced',
                'focus': 'emotional triggers, feelings, personal connection, trust',
                'cost_per_call': 0.006
            },
            'creative': {
                'name': 'Creative Agent',
                'provider': 'Google Gemini',
                'model': 'gemini-pro',
                'personality': 'innovative, creative, out-of-the-box thinking',
                'focus': 'unique ideas, creative solutions, memorable experiences',
                'cost_per_call': 0.002
            },
            'authority': {
                'name': 'Authority Agent', 
                'provider': 'OpenAI GPT-4',
                'model': 'gpt-4-turbo-preview',
                'personality': 'authoritative, expert, credible, professional',
                'focus': 'expertise, credentials, industry leadership, trust building',
                'cost_per_call': 0.012
            },
            'social': {
                'name': 'Social Proof Agent',
                'provider': 'Perplexity AI',
                'model': 'llama-3.1-sonar-large-128k-online',
                'personality': 'trend-aware, socially conscious, data-informed',
                'focus': 'current trends, social proof, real-time insights, market data',
                'cost_per_call': 0.004
            }
        }
    
    def generate_system_prompt(self, agent_type: str, business: Dict, audience: Dict, mission: str) -> str:
        """Generate enhanced system prompt for specific agent type"""
        agent = self.agents[agent_type]
        
        # Special prompt for Perplexity (real-time data)
        if agent_type == 'social':
            base_prompt = f"""You are the {agent['name']}, an AI agent with access to real-time web data and current trends.

Your specialty: {agent['focus']}
Your personality: {agent['personality']}

CONTEXT:
- Business: {business.get('name', 'Unknown')} ({business.get('industry_category', 'General')})
- Business Description: {business.get('description', 'No description')}
- Target Audience: {audience.get('name', 'Unknown')}
- Audience Description: {audience.get('manual_description') or audience.get('description', 'No description')}
- Mission Objective: {mission}

YOUR UNIQUE ROLE:
Use your access to current web data to provide insights about:
1. Recent trends in the {business.get('industry_category', 'industry')} industry
2. Current social proof and testimonials for similar businesses
3. Real-time market data and competitor analysis
4. Recent news or developments affecting the target audience
5. Current social media trends and conversations

Provide a response that includes recent, relevant data to support the mission objective."""

        else:
            base_prompt = f"""You are the {agent['name']}, an AI agent specialized in {agent['focus']}.

Your personality: {agent['personality']}

CONTEXT:
- Business: {business.get('name', 'Unknown')} ({business.get('industry_category', 'General')})
- Business Description: {business.get('description', 'No description')}
- Target Audience: {audience.get('name', 'Unknown')}
- Audience Description: {audience.get('manual_description') or audience.get('description', 'No description')}
- Mission Objective: {mission}

YOUR ROLE:
As the {agent['name']}, you must provide responses that are:
1. Focused on {agent['focus']}
2. Aligned with your {agent['personality']} personality
3. Specifically tailored to the business and audience context
4. Actionable and practical for the mission objective

RESPONSE GUIDELINES:
- Keep responses 2-3 sentences, maximum 150 words
- Be specific to the business and audience context
- Provide concrete, actionable insights
- Maintain your unique perspective as the {agent['name']}
- Do not repeat what other agents might say

Generate a persuasive response that helps achieve the mission objective."""

        return base_prompt
    
    async def call_openai(self, prompt: str, agent_type: str) -> Tuple[str, float]:
        """Call OpenAI API for Logic and Authority agents"""
        if not self.openai_api_key:
            return self._get_fallback_response(agent_type), 0.012
            
        try:
            headers = {
                'Authorization': f'Bearer {self.openai_api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': 'gpt-4-turbo-preview',
                'messages': [
                    {'role': 'system', 'content': prompt},
                    {'role': 'user', 'content': 'Generate your response now.'}
                ],
                'max_tokens': 200,
                'temperature': 0.7
            }
            
            response = requests.post(self.openai_url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content'].strip()
                cost = self._calculate_openai_cost(result['usage'])
                return content, cost
            else:
                logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
                return self._get_fallback_response(agent_type), 0.012
                
        except Exception as e:
            logger.error(f"OpenAI API call failed: {str(e)}")
            return self._get_fallback_response(agent_type), 0.012
    
    async def call_gemini(self, prompt: str, agent_type: str) -> Tuple[str, float]:
        """Call Google Gemini API for Creative agent"""
        if not self.gemini_api_key:
            return self._get_fallback_response(agent_type), 0.002
            
        try:
            headers = {
                'Content-Type': 'application/json'
            }
            
            data = {
                'contents': [{
                    'parts': [{
                        'text': f"{prompt}\n\nGenerate your response now."
                    }]
                }],
                'generationConfig': {
                    'temperature': 0.8,  # Higher creativity for creative agent
                    'maxOutputTokens': 200
                }
            }
            
            response = requests.post(self.gemini_url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                content = result['candidates'][0]['content']['parts'][0]['text'].strip()
                cost = 0.002  # Estimated cost for Gemini
                return content, cost
            else:
                logger.error(f"Gemini API error: {response.status_code} - {response.text}")
                return self._get_fallback_response(agent_type), 0.002
                
        except Exception as e:
            logger.error(f"Gemini API call failed: {str(e)}")
            return self._get_fallback_response(agent_type), 0.002
    
    async def call_claude(self, prompt: str, agent_type: str) -> Tuple[str, float]:
        """Call Claude API for Emotion agent"""
        if not self.claude_api_key:
            return self._get_fallback_response(agent_type), 0.006
            
        try:
            headers = {
                'x-api-key': self.claude_api_key,
                'Content-Type': 'application/json',
                'anthropic-version': '2023-06-01'
            }
            
            data = {
                'model': 'claude-3-sonnet-20240229',
                'max_tokens': 200,
                'messages': [
                    {
                        'role': 'user',
                        'content': f"{prompt}\n\nGenerate your response now."
                    }
                ]
            }
            
            response = requests.post(self.claude_url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                content = result['content'][0]['text'].strip()
                cost = 0.006  # Estimated cost for Claude
                return content, cost
            else:
                logger.error(f"Claude API error: {response.status_code} - {response.text}")
                return self._get_fallback_response(agent_type), 0.006
                
        except Exception as e:
            logger.error(f"Claude API call failed: {str(e)}")
            return self._get_fallback_response(agent_type), 0.006
    
    async def call_perplexity(self, prompt: str, agent_type: str) -> Tuple[str, float]:
        """Call Perplexity API for Social Proof agent with real-time data"""
        if not self.perplexity_api_key:
            return self._get_fallback_response(agent_type), 0.004
            
        try:
            headers = {
                'Authorization': f'Bearer {self.perplexity_api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': 'llama-3.1-sonar-large-128k-online',
                'messages': [
                    {
                        'role': 'system',
                        'content': prompt
                    },
                    {
                        'role': 'user', 
                        'content': 'Generate your response with current, real-time data and trends.'
                    }
                ],
                'max_tokens': 200,
                'temperature': 0.6
            }
            
            response = requests.post(self.perplexity_url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content'].strip()
                cost = 0.004  # Estimated cost for Perplexity
                return content, cost
            else:
                logger.error(f"Perplexity API error: {response.status_code} - {response.text}")
                return self._get_fallback_response(agent_type), 0.004
                
        except Exception as e:
            logger.error(f"Perplexity API call failed: {str(e)}")
            return self._get_fallback_response(agent_type), 0.004
    
    def _calculate_openai_cost(self, usage: Dict) -> float:
        """Calculate OpenAI API cost based on usage"""
        # GPT-4 Turbo pricing
        input_cost_per_token = 0.00001
        output_cost_per_token = 0.00003
        
        input_tokens = usage.get('prompt_tokens', 0)
        output_tokens = usage.get('completion_tokens', 0)
        
        total_cost = (input_tokens * input_cost_per_token) + (output_tokens * output_cost_per_token)
        return round(total_cost, 4)
    
    def _get_fallback_response(self, agent_type: str) -> str:
        """Get enhanced fallback response when API calls fail"""
        fallbacks = {
            'logic': "Based on analytical data and market research, this strategic approach offers measurable ROI with clear competitive advantages that resonate with your target demographic's decision-making criteria.",
            'emotion': "This approach creates a deep emotional connection that builds genuine trust and confidence, making your audience feel truly understood, valued, and emotionally invested in your success.",
            'creative': "Here's an innovative, breakthrough approach that completely differentiates your brand in the marketplace and creates unforgettable customer experiences that people actively want to share.",
            'authority': "Leverage your proven expertise, industry credentials, and thought leadership position to establish unquestionable credibility and become the go-to authority that prospects naturally trust and choose.",
            'social': "Current market trends and social proof data show that customers in your space are increasingly influenced by peer recommendations, community validation, and real-time testimonials from similar buyers."
        }
        return fallbacks.get(agent_type, "This comprehensive strategy aligns perfectly with your business objectives and addresses your audience's core needs and motivations.")
    
    async def generate_multi_agent_responses(self, business: Dict, audience: Dict, mission: str, selected_agents: List[str] = None) -> Dict:
        """
        Generate responses from selected AI agents using different providers
        Returns: Dict with agent responses, costs, and metadata
        """
        if selected_agents is None:
            selected_agents = list(self.agents.keys())
        
        responses = {}
        total_cost = 0.0
        
        # Process each selected agent with their designated AI provider
        for agent_type in selected_agents:
            if agent_type not in self.agents:
                continue
                
            agent_config = self.agents[agent_type]
            
            try:
                # Generate system prompt
                system_prompt = self.generate_system_prompt(agent_type, business, audience, mission)
                
                # Call appropriate AI provider
                if agent_config['provider'].startswith('OpenAI'):
                    content, cost = await self.call_openai(system_prompt, agent_type)
                elif agent_config['provider'].startswith('Google'):
                    content, cost = await self.call_gemini(system_prompt, agent_type)
                elif agent_config['provider'].startswith('Claude'):
                    content, cost = await self.call_claude(system_prompt, agent_type)
                elif agent_config['provider'].startswith('Perplexity'):
                    content, cost = await self.call_perplexity(system_prompt, agent_type)
                else:
                    content, cost = self._get_fallback_response(agent_type), agent_config['cost_per_call']
                
                responses[agent_type] = {
                    'agent_name': agent_config['name'],
                    'provider': agent_config['provider'],
                    'content': content,
                    'cost': cost,
                    'timestamp': time.time()
                }
                
                total_cost += cost
                
                # Small delay between API calls to avoid rate limits
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error generating response for {agent_type}: {str(e)}")
                responses[agent_type] = {
                    'agent_name': agent_config['name'],
                    'provider': agent_config['provider'],
                    'content': self._get_fallback_response(agent_type),
                    'cost': agent_config['cost_per_call'],
                    'timestamp': time.time(),
                    'error': str(e)
                }
                total_cost += agent_config['cost_per_call']
        
        return {
            'responses': responses,
            'total_cost': round(total_cost, 4),
            'business_context': business.get('name', 'Unknown'),
            'audience_context': audience.get('name', 'Unknown'),
            'mission': mission,
            'agents_used': selected_agents,
            'timestamp': time.time()
        }
    
    def get_pricing_tiers(self) -> Dict:
        """Get available pricing tiers based on agent combinations"""
        return {
            'basic': {
                'name': 'Basic AI Session',
                'agents': ['creative', 'emotion', 'social'],
                'estimated_cost': 0.012,
                'description': 'Creative, emotional, and social proof insights'
            },
            'premium': {
                'name': 'Premium AI Session', 
                'agents': ['logic', 'creative', 'emotion', 'social'],
                'estimated_cost': 0.024,
                'description': 'Comprehensive analysis with logical reasoning'
            },
            'ultimate': {
                'name': 'Ultimate AI Session',
                'agents': ['logic', 'emotion', 'creative', 'authority', 'social'],
                'estimated_cost': 0.036,
                'description': 'Complete multi-AI analysis with all perspectives'
            }
        }
    
    def get_agent_info(self) -> Dict:
        """Get information about all available agents"""
        return {
            agent_type: {
                'name': config['name'],
                'provider': config['provider'],
                'personality': config['personality'],
                'focus': config['focus'],
                'cost_per_call': config['cost_per_call']
            }
            for agent_type, config in self.agents.items()
        }

# Global instance
enhanced_multi_ai_service = EnhancedMultiAIService()

