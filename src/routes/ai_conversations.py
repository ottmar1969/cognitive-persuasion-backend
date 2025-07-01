"""
AI Conversations Blueprint
Integrates real AI-to-AI conversation system into existing cognitive-persuasion backend
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

from flask import Blueprint, request, jsonify
from flask_socketio import emit, join_room, leave_room
import openai
import anthropic
import google.generativeai as genai
import requests
import os

# Create blueprint
ai_conversations_bp = Blueprint('ai_conversations', __name__)

# AI Configuration
@dataclass
class AIConfig:
    openai_api_key: str
    anthropic_api_key: str
    google_api_key: str
    perplexity_api_key: str

class ConversationState(Enum):
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"

@dataclass
class AIAgent:
    name: str
    model: str
    role: str
    api_service: str
    personality: str

@dataclass
class ConversationMessage:
    id: str
    agent_name: str
    content: str
    timestamp: datetime
    conversation_id: str
    business_id: str

class AIConversationEngine:
    """
    AI-to-AI conversation engine integrated with existing business system
    """
    
    def __init__(self):
        self.active_conversations: Dict[str, Dict] = {}
        self.conversation_history: Dict[str, List[ConversationMessage]] = {}
        
        # Get API keys from environment
        self.ai_config = AIConfig(
            openai_api_key=os.getenv('OPENAI_API_KEY', ''),
            anthropic_api_key=os.getenv('ANTHROPIC_API_KEY', ''),
            google_api_key=os.getenv('GOOGLE_API_KEY', ''),
            perplexity_api_key=os.getenv('PERPLEXITY_API_KEY', '')
        )
        
        # Initialize AI clients if keys are available
        self.openai_client = None
        self.anthropic_client = None
        self.gemini_model = None
        
        if self.ai_config.openai_api_key:
            self.openai_client = openai.OpenAI(api_key=self.ai_config.openai_api_key)
        
        if self.ai_config.anthropic_api_key:
            self.anthropic_client = anthropic.Anthropic(api_key=self.ai_config.anthropic_api_key)
        
        if self.ai_config.google_api_key:
            genai.configure(api_key=self.ai_config.google_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-pro')
        
        # Define AI agents
        self.ai_agents = {
            "promoter": AIAgent(
                name="Business Promoter",
                model="gpt-4",
                role="Advocate for the business with factual, compelling arguments",
                api_service="openai",
                personality="Professional, enthusiastic, fact-focused"
            ),
            "challenger": AIAgent(
                name="Critical Analyst", 
                model="claude-3-sonnet",
                role="Ask tough questions and challenge claims objectively",
                api_service="anthropic",
                personality="Analytical, skeptical, thorough"
            ),
            "mediator": AIAgent(
                name="Neutral Evaluator",
                model="gemini-pro",
                role="Provide balanced analysis and mediate discussions",
                api_service="google",
                personality="Balanced, objective, comprehensive"
            ),
            "researcher": AIAgent(
                name="Market Researcher",
                model="llama-3.1-sonar-large-128k-online",
                role="Provide real-time market data and competitive analysis",
                api_service="perplexity",
                personality="Data-driven, current, factual"
            )
        }
    
    async def call_openai_api(self, prompt: str, context: List[Dict]) -> str:
        """Real OpenAI API call"""
        if not self.openai_client:
            return "OpenAI API key not configured"
        
        try:
            messages = [{"role": "system", "content": prompt}]
            messages.extend(context[-5:])  # Last 5 messages for context
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"OpenAI API Error: {str(e)}"
    
    async def call_anthropic_api(self, prompt: str, context: List[Dict]) -> str:
        """Real Anthropic Claude API call"""
        if not self.anthropic_client:
            return "Anthropic API key not configured"
        
        try:
            conversation = ""
            for msg in context[-5:]:  # Last 5 messages
                conversation += f"{msg['role']}: {msg['content']}\n"
            
            full_prompt = f"{prompt}\n\nConversation so far:\n{conversation}\n\nYour response:"
            
            response = self.anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=500,
                messages=[{"role": "user", "content": full_prompt}]
            )
            return response.content[0].text
        except Exception as e:
            return f"Anthropic API Error: {str(e)}"
    
    async def call_gemini_api(self, prompt: str, context: List[Dict]) -> str:
        """Real Google Gemini API call"""
        if not self.gemini_model:
            return "Google API key not configured"
        
        try:
            conversation = ""
            for msg in context[-5:]:  # Last 5 messages
                conversation += f"{msg['role']}: {msg['content']}\n"
            
            full_prompt = f"{prompt}\n\nConversation context:\n{conversation}\n\nProvide your balanced analysis:"
            
            response = self.gemini_model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            return f"Gemini API Error: {str(e)}"
    
    async def call_perplexity_api(self, prompt: str, context: List[Dict]) -> str:
        """Real Perplexity API call for current market data"""
        if not self.ai_config.perplexity_api_key:
            return "Perplexity API key not configured"
        
        try:
            headers = {
                "Authorization": f"Bearer {self.ai_config.perplexity_api_key}",
                "Content-Type": "application/json"
            }
            
            messages = [{"role": "system", "content": prompt}]
            messages.extend(context[-3:])  # Last 3 messages for context
            
            data = {
                "model": "llama-3.1-sonar-large-128k-online",
                "messages": messages,
                "max_tokens": 500,
                "temperature": 0.3
            }
            
            response = requests.post(
                "https://api.perplexity.ai/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                return f"Perplexity API Error: {response.status_code}"
        except Exception as e:
            return f"Perplexity API Error: {str(e)}"
    
    async def start_conversation(self, business_data: Dict) -> str:
        """Start a real AI-to-AI conversation about a business"""
        conversation_id = str(uuid.uuid4())
        
        # Initialize conversation state
        self.active_conversations[conversation_id] = {
            "id": conversation_id,
            "business_data": business_data,
            "state": ConversationState.RUNNING,
            "current_round": 1,
            "max_rounds": 8,
            "participants": list(self.ai_agents.keys()),
            "context": []
        }
        
        self.conversation_history[conversation_id] = []
        
        # Start the conversation
        await self._run_conversation_round(conversation_id)
        
        return conversation_id
    
    async def _run_conversation_round(self, conversation_id: str):
        """Execute one round of real AI-to-AI conversation"""
        if conversation_id not in self.active_conversations:
            return
        
        conv = self.active_conversations[conversation_id]
        business = conv["business_data"]
        
        if conv["state"] != ConversationState.RUNNING:
            return
        
        # Round 1: Promoter introduces the business
        if conv["current_round"] == 1:
            prompt = f"""
            You are a professional business promoter. Present {business.get('name', 'this business')} in a compelling but factual way.
            
            Business Details:
            - Name: {business.get('name', 'Unknown')}
            - Industry: {business.get('industry', 'Not specified')}
            - Description: {business.get('description', 'No description available')}
            - Target Audience: {business.get('target_audience', 'General market')}
            
            Provide a professional introduction highlighting why this business stands out.
            Be factual, specific, and compelling. No exaggeration or false claims.
            Keep response under 200 words.
            """
            
            response = await self.call_openai_api(prompt, conv["context"])
            await self._add_message(conversation_id, "promoter", response)
        
        # Round 2: Challenger asks critical questions
        elif conv["current_round"] == 2:
            prompt = f"""
            You are a critical business analyst. Review the business presentation and ask tough, 
            relevant questions about {business.get('name', 'this business')}.
            
            Focus on:
            - Market positioning and competitive advantages
            - Value proposition validation
            - Target audience fit
            - Business model sustainability
            
            Ask 2-3 specific, professional questions that any serious buyer would ask.
            Keep response under 150 words.
            """
            
            response = await self.call_anthropic_api(prompt, conv["context"])
            await self._add_message(conversation_id, "challenger", response)
        
        # Round 3: Researcher provides market data
        elif conv["current_round"] == 3:
            prompt = f"""
            Provide current market research and competitive analysis for {business.get('name', 'this business')} 
            in the {business.get('industry', 'specified')} industry.
            
            Research:
            - Current market trends in {business.get('industry', 'this')} industry
            - Competitive landscape analysis
            - Industry growth projections
            - Target audience behavior patterns
            
            Use real, current data. Be factual and cite sources when possible.
            Keep response under 200 words.
            """
            
            response = await self.call_perplexity_api(prompt, conv["context"])
            await self._add_message(conversation_id, "researcher", response)
        
        # Round 4: Mediator provides balanced analysis
        elif conv["current_round"] == 4:
            prompt = f"""
            You are a neutral business evaluator. Provide a balanced analysis of the discussion about {business.get('name', 'this business')}.
            
            Consider:
            - Strengths highlighted by the promoter
            - Valid concerns raised by the analyst
            - Market data provided by the researcher
            - Overall business viability
            
            Provide an objective assessment with both positives and areas for improvement.
            Keep response under 200 words.
            """
            
            response = await self.call_gemini_api(prompt, conv["context"])
            await self._add_message(conversation_id, "mediator", response)
        
        # Continue with additional rounds...
        elif conv["current_round"] <= conv["max_rounds"]:
            # Rotate between agents for continued discussion
            agent_keys = list(self.ai_agents.keys())
            current_agent = agent_keys[(conv["current_round"] - 1) % len(agent_keys)]
            
            prompt = f"""
            Continue the professional discussion about {business.get('name', 'this business')}.
            Build on the previous conversation and provide additional insights.
            Keep response under 150 words and maintain your role as {self.ai_agents[current_agent].role}.
            """
            
            if current_agent == "promoter":
                response = await self.call_openai_api(prompt, conv["context"])
            elif current_agent == "challenger":
                response = await self.call_anthropic_api(prompt, conv["context"])
            elif current_agent == "mediator":
                response = await self.call_gemini_api(prompt, conv["context"])
            else:  # researcher
                response = await self.call_perplexity_api(prompt, conv["context"])
            
            await self._add_message(conversation_id, current_agent, response)
        
        # Schedule next round or complete conversation
        conv["current_round"] += 1
        
        if conv["current_round"] <= conv["max_rounds"] and conv["state"] == ConversationState.RUNNING:
            # Schedule next round with delay
            await asyncio.sleep(3)  # 3 second pause between responses
            await self._run_conversation_round(conversation_id)
        else:
            conv["state"] = ConversationState.COMPLETED
    
    async def _add_message(self, conversation_id: str, agent_key: str, content: str):
        """Add a message to the conversation history"""
        agent = self.ai_agents[agent_key]
        message = ConversationMessage(
            id=str(uuid.uuid4()),
            agent_name=agent.name,
            content=content,
            timestamp=datetime.now(),
            conversation_id=conversation_id,
            business_id=self.active_conversations[conversation_id]["business_data"].get("id", "unknown")
        )
        
        self.conversation_history[conversation_id].append(message)
        
        # Add to context for next AI calls
        self.active_conversations[conversation_id]["context"].append({
            "role": agent.name,
            "content": content
        })
        
        # Emit real-time update (will be handled by SocketIO)
        # This will be implemented in the main app
    
    def pause_conversation(self, conversation_id: str) -> bool:
        """Pause an active conversation"""
        if conversation_id in self.active_conversations:
            self.active_conversations[conversation_id]["state"] = ConversationState.PAUSED
            return True
        return False
    
    def resume_conversation(self, conversation_id: str) -> bool:
        """Resume a paused conversation"""
        if conversation_id in self.active_conversations:
            conv = self.active_conversations[conversation_id]
            if conv["state"] == ConversationState.PAUSED:
                conv["state"] = ConversationState.RUNNING
                # Continue from where it left off
                asyncio.create_task(self._run_conversation_round(conversation_id))
                return True
        return False
    
    def stop_conversation(self, conversation_id: str) -> bool:
        """Stop a conversation completely"""
        if conversation_id in self.active_conversations:
            self.active_conversations[conversation_id]["state"] = ConversationState.STOPPED
            return True
        return False
    
    def get_conversation_status(self, conversation_id: str) -> Dict:
        """Get real-time conversation status"""
        if conversation_id not in self.active_conversations:
            return {"error": "Conversation not found"}
        
        conv = self.active_conversations[conversation_id]
        messages = self.conversation_history.get(conversation_id, [])
        
        return {
            "conversation_id": conversation_id,
            "business_id": conv["business_data"].get("id", "unknown"),
            "business_name": conv["business_data"].get("name", "Unknown"),
            "state": conv["state"].value,
            "current_round": conv["current_round"],
            "max_rounds": conv["max_rounds"],
            "total_messages": len(messages),
            "last_activity": messages[-1].timestamp.isoformat() if messages else None,
            "participants": [agent.name for agent in self.ai_agents.values()]
        }
    
    def get_live_messages(self, conversation_id: str) -> List[Dict]:
        """Get live conversation messages"""
        messages = self.conversation_history.get(conversation_id, [])
        return [
            {
                "id": msg.id,
                "agent_name": msg.agent_name,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in messages
        ]

# Initialize the conversation engine
conversation_engine = AIConversationEngine()

# Routes
@ai_conversations_bp.route('/start', methods=['POST'])
def start_conversation():
    """Start a real AI conversation for a business"""
    try:
        data = request.json
        business_id = data.get('business_id')
        
        if not business_id:
            return jsonify({"error": "business_id is required"}), 400
        
        # Get business data from the existing business system
        # This integrates with the existing business routes
        from src.models.user_simple import Business
        business = Business.query.filter_by(id=business_id).first()
        
        if not business:
            return jsonify({"error": "Business not found"}), 404
        
        # Convert business to dict for AI processing
        business_data = {
            "id": business.id,
            "name": business.name,
            "description": business.description,
            "industry": business.industry,
            "target_audience": business.target_audience,
            "unique_selling_points": business.unique_selling_points.split(',') if business.unique_selling_points else []
        }
        
        # Start the conversation
        conversation_id = asyncio.run(conversation_engine.start_conversation(business_data))
        
        return jsonify({
            "conversation_id": conversation_id,
            "status": "started",
            "message": "Real AI-to-AI conversation initiated",
            "business_name": business.name
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ai_conversations_bp.route('/<conversation_id>/pause', methods=['POST'])
def pause_conversation(conversation_id):
    """Pause conversation with context preservation"""
    success = conversation_engine.pause_conversation(conversation_id)
    return jsonify({"success": success, "status": "paused"})

@ai_conversations_bp.route('/<conversation_id>/resume', methods=['POST'])
def resume_conversation(conversation_id):
    """Resume paused conversation"""
    success = conversation_engine.resume_conversation(conversation_id)
    return jsonify({"success": success, "status": "resumed"})

@ai_conversations_bp.route('/<conversation_id>/stop', methods=['POST'])
def stop_conversation(conversation_id):
    """Stop conversation completely"""
    success = conversation_engine.stop_conversation(conversation_id)
    return jsonify({"success": success, "status": "stopped"})

@ai_conversations_bp.route('/<conversation_id>/status', methods=['GET'])
def get_conversation_status(conversation_id):
    """Get real-time conversation status"""
    status = conversation_engine.get_conversation_status(conversation_id)
    return jsonify(status)

@ai_conversations_bp.route('/<conversation_id>/messages', methods=['GET'])
def get_conversation_messages(conversation_id):
    """Get live conversation messages"""
    messages = conversation_engine.get_live_messages(conversation_id)
    return jsonify({"messages": messages})

@ai_conversations_bp.route('/active', methods=['GET'])
def get_active_conversations():
    """Get all active conversations"""
    active = []
    for conv_id, conv_data in conversation_engine.active_conversations.items():
        if conv_data["state"] in [ConversationState.RUNNING, ConversationState.PAUSED]:
            active.append({
                "conversation_id": conv_id,
                "business_name": conv_data["business_data"].get("name", "Unknown"),
                "state": conv_data["state"].value,
                "current_round": conv_data["current_round"]
            })
    
    return jsonify({"active_conversations": active})

# Health check for AI services
@ai_conversations_bp.route('/health', methods=['GET'])
def ai_health_check():
    """Check AI service availability"""
    services = {
        "openai": bool(conversation_engine.ai_config.openai_api_key),
        "anthropic": bool(conversation_engine.ai_config.anthropic_api_key),
        "google": bool(conversation_engine.ai_config.google_api_key),
        "perplexity": bool(conversation_engine.ai_config.perplexity_api_key)
    }
    
    return jsonify({
        "status": "healthy",
        "ai_services": services,
        "active_conversations": len(conversation_engine.active_conversations)
    })

