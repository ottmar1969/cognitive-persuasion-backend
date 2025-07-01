"""
AI Conversations Blueprint - Simplified Version (No External AI Dependencies)
Integrates AI conversation system into existing cognitive-persuasion backend
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

from flask import Blueprint, request, jsonify
import os

# Create blueprint
ai_conversations_bp = Blueprint('ai_conversations', __name__)

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
    AI-to-AI conversation engine with simulated responses (for demo)
    """
    
    def __init__(self):
        self.active_conversations: Dict[str, Dict] = {}
        self.conversation_history: Dict[str, List[ConversationMessage]] = {}
        
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
    
    def generate_ai_response(self, agent_key: str, business_data: Dict, round_num: int) -> str:
        """Generate simulated AI responses for demo purposes"""
        business_name = business_data.get('name', 'this business')
        industry = business_data.get('industry_category', 'the industry')
        description = business_data.get('description', 'No description available')
        
        responses = {
            "promoter": {
                1: f"I'm excited to present {business_name}, a standout company in {industry}. {description} What makes {business_name} exceptional is their commitment to innovation and customer satisfaction. They've positioned themselves uniquely in the market by focusing on quality and reliability. Their approach to business demonstrates clear value proposition and sustainable growth potential.",
                2: f"Let me address those concerns about {business_name}. Their competitive advantage lies in their deep understanding of {industry} dynamics. They've built strong customer relationships and have a proven track record of delivering results. The market validation speaks for itself through their growing customer base and positive feedback.",
                3: f"Building on the market research, {business_name} is perfectly positioned to capitalize on current {industry} trends. Their business model aligns with market demands and they have the expertise to execute their vision effectively.",
                4: f"In conclusion, {business_name} represents a solid investment opportunity in {industry}. They combine market knowledge, operational excellence, and strategic vision to deliver consistent value to their customers."
            },
            "challenger": {
                1: f"While the presentation of {business_name} sounds promising, I have several critical questions. What specific metrics demonstrate their market leadership in {industry}? How do they differentiate from established competitors? What evidence supports their claimed competitive advantages?",
                2: f"I appreciate the enthusiasm, but let's examine the fundamentals. What's their customer acquisition cost versus lifetime value? How sustainable is their current business model in a competitive {industry} landscape? What are the potential risks and challenges they face?",
                3: f"The market data is interesting, but how does {business_name} specifically capture this opportunity? What's their go-to-market strategy? Do they have the resources and capabilities to execute at scale?",
                4: f"Before making any conclusions about {business_name}, we need to see concrete evidence of performance, clear financial projections, and a realistic assessment of market challenges in {industry}."
            },
            "mediator": {
                1: f"Thank you both for your perspectives on {business_name}. This {industry} company presents both opportunities and challenges that deserve balanced consideration. Let's examine the facts objectively and consider multiple viewpoints.",
                2: f"I see valid points from both sides regarding {business_name}. The enthusiasm is warranted given their {industry} focus, but the critical questions raised are equally important for a complete assessment.",
                3: f"The market research provides valuable context for {business_name}'s position in {industry}. We should weigh both the opportunities and the competitive challenges they face.",
                4: f"Based on our discussion, {business_name} shows promise in {industry} but requires careful due diligence. Both the strengths and potential concerns merit serious consideration."
            },
            "researcher": {
                1: f"Current market analysis shows {industry} is experiencing significant growth trends. Key factors include increasing demand, technological advancement, and evolving customer preferences. {business_name} operates in a market segment with strong fundamentals.",
                2: f"Competitive landscape analysis reveals {industry} has both established players and emerging companies. Market size is expanding, with projected growth rates indicating positive outlook for well-positioned companies like {business_name}.",
                3: f"Recent industry reports highlight {industry} trends that favor companies with {business_name}'s positioning. Consumer behavior data supports demand for their type of services/products.",
                4: f"Market research conclusion: {industry} presents viable opportunities for companies with strong execution capabilities. {business_name} operates in a favorable market environment with growth potential."
            }
        }
        
        agent_responses = responses.get(agent_key, {})
        return agent_responses.get(round_num, f"Continuing the discussion about {business_name} in {industry}...")
    
    def start_conversation(self, business_data: Dict) -> str:
        """Start a simulated AI-to-AI conversation about a business"""
        conversation_id = str(uuid.uuid4())
        
        # Initialize conversation state
        self.active_conversations[conversation_id] = {
            "id": conversation_id,
            "business_data": business_data,
            "state": ConversationState.RUNNING,
            "current_round": 1,
            "max_rounds": 4,
            "participants": list(self.ai_agents.keys()),
            "context": []
        }
        
        self.conversation_history[conversation_id] = []
        
        # Generate initial messages for demo
        self._generate_conversation_messages(conversation_id)
        
        return conversation_id
    
    def _generate_conversation_messages(self, conversation_id: str):
        """Generate simulated conversation messages"""
        if conversation_id not in self.active_conversations:
            return
        
        conv = self.active_conversations[conversation_id]
        business_data = conv["business_data"]
        
        # Generate messages for each round
        for round_num in range(1, conv["max_rounds"] + 1):
            for agent_key in ["promoter", "challenger", "researcher", "mediator"]:
                content = self.generate_ai_response(agent_key, business_data, round_num)
                self._add_message(conversation_id, agent_key, content)
        
        # Mark as completed
        conv["state"] = ConversationState.COMPLETED
    
    def _add_message(self, conversation_id: str, agent_key: str, content: str):
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
        
        # Add to context
        self.active_conversations[conversation_id]["context"].append({
            "role": agent.name,
            "content": content
        })
    
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
    """Start a simulated AI conversation for a business"""
    try:
        data = request.json
        business_id = data.get('business_id')
        
        if not business_id:
            return jsonify({"error": "business_id is required"}), 400
        
        # Get business data from the existing business system
        try:
            from src.models.user_simple import Business
            business = Business.query.filter_by(id=business_id).first()
        except:
            # Fallback if model import fails
            business = None
        
        if not business:
            return jsonify({"error": "Business not found"}), 404
        
        # Convert business to dict for AI processing
        business_data = {
            "id": business.id,
            "name": business.name,
            "description": business.description,
            "industry_category": getattr(business, 'industry_category', 'General'),
        }
        
        # Start the conversation
        conversation_id = conversation_engine.start_conversation(business_data)
        
        return jsonify({
            "conversation_id": conversation_id,
            "status": "started",
            "message": "AI-to-AI conversation simulation initiated",
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
    return jsonify({
        "status": "healthy",
        "mode": "simulation",
        "message": "AI conversation simulation ready",
        "active_conversations": len(conversation_engine.active_conversations)
    })

