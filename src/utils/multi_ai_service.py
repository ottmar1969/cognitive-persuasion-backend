import os
import requests
import json
import time
from typing import Dict, List, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MultiAIService:
    """
    Multi-AI service that integrates OpenAI, Google Gemini, and Claude
    for diverse AI agent responses in persuasion conversations.
    """
    
    def __init__(self):
        # API Keys (should be set in environment variables)
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.gemini_api_key = os.getenv('GEMINI_API_KEY') 
        self.claude_api_key = os.getenv('CLAUDE_API_KEY')
        
        # API Endpoints
        self.openai_url = "https://api.openai.com/v1/chat/completions"
        self.gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={self.gemini_api_key}"
        self.claude_url = "https://api.anthropic.com/v1/messages"
        
        # Agent configurations
        self.agents = {
            'logic': {
                'name': 'Logic Agent',
                'provider': 'OpenAI GPT-4',
                'model': 'gpt-4',
                'personality': 'analytical, data-driven, logical reasoning',
                'focus': 'facts, statistics, logical arguments, ROI analysis'
            },
            'emotion': {
                'name': 'Emotion Agent',
                'provider': 'OpenAI GPT-4',
                'model': 'gpt-4', 
                'personality': 'empathetic, emotionally intelligent, persuasive',
                'focus': 'emotional triggers, feelings, personal connection, trust'
            },
            'creative': {
                'name': 'Creative Agent',
                'provider': 'Google Gemini',
                'model': 'gemini-pro',
                'personality': 'innovative, creative, out-of-the-box thinking',
                'focus': 'unique ideas, creative solutions, memorable experiences'
            },
            'authority': {
                'name': 'Authority Agent', 
                'provider': 'Google Gemini',
                'model': 'gemini-pro',
                'personality': 'authoritative, expert, credible, professional',
                'focus': 'expertise, credentials, industry leadership, trust building'
            },
            'social': {
                'name': 'Social Proof Agent',
                'provider': 'Claude (Anthropic)',
                'model': 'claude-3-sonnet-20240229',
                'personality': 'community-focused, social validation, peer influence',
                'focus': 'testimonials, social proof, community, peer recommendations'
            }
        }
    
    def generate_system_prompt(self, agent_type: str, business: Dict, audience: Dict, mission: str) -> str:
        """Generate system prompt for specific agent type"""
        agent = self.agents[agent_type]
        
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
        """Call OpenAI API for Logic and Emotion agents"""
        if not self.openai_api_key:
            return self._get_fallback_response(agent_type), 0.01
            
        try:
            headers = {
                'Authorization': f'Bearer {self.openai_api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': 'gpt-4',
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
                return self._get_fallback_response(agent_type), 0.01
                
        except Exception as e:
            logger.error(f"OpenAI API call failed: {str(e)}")
            return self._get_fallback_response(agent_type), 0.01
    
    async def call_gemini(self, prompt: str, agent_type: str) -> Tuple[str, float]:
        """Call Google Gemini API for Creative and Authority agents"""
        if not self.gemini_api_key:
            return self._get_fallback_response(agent_type), 0.01
            
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
                    'temperature': 0.7,
                    'maxOutputTokens': 200
                }
            }
            
            response = requests.post(self.gemini_url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                content = result['candidates'][0]['content']['parts'][0]['text'].strip()
                cost = 0.005  # Estimated cost for Gemini
                return content, cost
            else:
                logger.error(f"Gemini API error: {response.status_code} - {response.text}")
                return self._get_fallback_response(agent_type), 0.01
                
        except Exception as e:
            logger.error(f"Gemini API call failed: {str(e)}")
            return self._get_fallback_response(agent_type), 0.01
    
    async def call_claude(self, prompt: str, agent_type: str) -> Tuple[str, float]:
        """Call Claude API for Social Proof agent"""
        if not self.claude_api_key:
            return self._get_fallback_response(agent_type), 0.01
            
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
                cost = 0.008  # Estimated cost for Claude
                return content, cost
            else:
                logger.error(f"Claude API error: {response.status_code} - {response.text}")
                return self._get_fallback_response(agent_type), 0.01
                
        except Exception as e:
            logger.error(f"Claude API call failed: {str(e)}")
            return self._get_fallback_response(agent_type), 0.01
    
    def _calculate_openai_cost(self, usage: Dict) -> float:
        """Calculate OpenAI API cost based on usage"""
        # GPT-4 pricing (approximate)
        input_cost_per_token = 0.00003
        output_cost_per_token = 0.00006
        
        input_tokens = usage.get('prompt_tokens', 0)
        output_tokens = usage.get('completion_tokens', 0)
        
        total_cost = (input_tokens * input_cost_per_token) + (output_tokens * output_cost_per_token)
        return round(total_cost, 4)
    
    def _get_fallback_response(self, agent_type: str) -> str:
        """Get fallback response when API calls fail"""
        fallbacks = {
            'logic': "Based on analytical data, this approach offers measurable ROI and clear competitive advantages for your target market.",
            'emotion': "This creates an emotional connection that builds trust and confidence, making customers feel valued and understood.",
            'creative': "Here's an innovative approach that differentiates your brand and creates memorable customer experiences.",
            'authority': "Leverage your expertise and industry credentials to establish thought leadership and build credibility with prospects.",
            'social': "Social proof through testimonials and community validation significantly influences decision-making in your target audience."
        }
        return fallbacks.get(agent_type, "This strategy aligns with your business objectives and audience needs.")
    
    async def generate_multi_agent_responses(self, business: Dict, audience: Dict, mission: str) -> Dict:
        """
        Generate responses from all AI agents using different providers
        Returns: Dict with agent responses, costs, and metadata
        """
        responses = {}
        total_cost = 0.0
        
        # Process each agent with their designated AI provider
        for agent_type, agent_config in self.agents.items():
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
                else:
                    content, cost = self._get_fallback_response(agent_type), 0.01
                
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
                    'cost': 0.01,
                    'timestamp': time.time(),
                    'error': str(e)
                }
                total_cost += 0.01
        
        return {
            'responses': responses,
            'total_cost': round(total_cost, 4),
            'business_context': business.get('name', 'Unknown'),
            'audience_context': audience.get('name', 'Unknown'),
            'mission': mission,
            'timestamp': time.time()
        }
    
    def get_agent_info(self) -> Dict:
        """Get information about all available agents"""
        return {
            agent_type: {
                'name': config['name'],
                'provider': config['provider'],
                'personality': config['personality'],
                'focus': config['focus']
            }
            for agent_type, config in self.agents.items()
        }

# Global instance
multi_ai_service = MultiAIService()

