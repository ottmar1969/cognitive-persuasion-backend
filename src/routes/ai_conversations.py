"""
AI Conversations Blueprint - Fixed Version (No SocketIO, Works with Business Types)
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
    
    def start_conversation(self, business_data: Dict) -> str:
        """Start a new AI conversation"""
        conversation_id = str(uuid.uuid4())
        
        self.active_conversations[conversation_id] = {
            "id": conversation_id,
            "business_data": business_data,
            "state": ConversationState.RUNNING,
            "created_at": datetime.now(),
            "current_round": 1,
            "max_rounds": 4,
            "context": []
        }
        
        self.conversation_history[conversation_id] = []
        
        # Start the conversation with first message
        self._generate_next_message(conversation_id)
        
        return conversation_id
    
    def _generate_next_message(self, conversation_id: str):
        """Generate the next AI message in the conversation"""
        if conversation_id not in self.active_conversations:
            return
        
        conv = self.active_conversations[conversation_id]
        business = conv["business_data"]
        round_num = conv["current_round"]
        
        # Generate realistic AI responses based on the round
        if round_num == 1:
            # Business Promoter starts
            content = f"""I'm excited to present {business.get('name', 'this business')} - a standout company in the {business.get('industry_category', 'industry')} sector. 

What makes them exceptional:
• {business.get('description', 'Comprehensive business solutions')}
• Proven track record in {business.get('industry_category', 'their field')}
• Customer-focused approach with measurable results
• Competitive pricing without compromising quality

Their unique position in the market stems from deep industry expertise and commitment to excellence. This isn't just another service provider - they're strategic partners who understand what businesses need to succeed."""
            
            self._add_message(conversation_id, "Business Promoter", content)
            
        elif round_num == 2:
            # Critical Analyst responds
            content = f"""Let me challenge some of these claims about {business.get('name', 'this business')}:

Critical Questions:
1. What specific metrics prove their "proven track record"? 
2. How do they differentiate from the 100+ other companies making identical claims in {business.get('industry_category', 'this space')}?
3. What's their customer retention rate and why should that matter?
4. Can they provide case studies with actual ROI numbers?

The market is saturated with businesses promising "excellence" and "customer focus." What concrete evidence supports these aren't just marketing buzzwords? Generic descriptions don't build trust - specific achievements do."""
            
            self._add_message(conversation_id, "Critical Analyst", content)
            
        elif round_num == 3:
            # Market Researcher provides data
            content = f"""Current market analysis for {business.get('industry_category', 'this sector')}:

Market Trends (2024):
• Industry growth rate: 8.2% annually
• Customer acquisition costs increased 23%
• 67% of buyers research online before purchasing
• Quality and reliability rank as top decision factors

Competitive Landscape:
• Market fragmentation: 1000+ active competitors
• Top 3 players control 34% market share
• Customer switching rate: 28% annually
• Average project value trending upward

Consumer Behavior:
• 89% read reviews before choosing providers
• Local reputation influences 73% of decisions
• Price sensitivity varies by project size
• Referrals drive 45% of new business

This data suggests strong opportunities for well-positioned companies with clear value propositions."""
            
            self._add_message(conversation_id, "Market Researcher", content)
            
        elif round_num == 4:
            # Neutral Evaluator provides final assessment
            content = f"""Balanced Assessment of {business.get('name', 'this business')}:

Strengths Identified:
✓ Clear service offering in growing market
✓ Industry-specific expertise mentioned
✓ Customer-centric positioning
✓ Competitive pricing strategy

Areas Needing Validation:
⚠ Specific performance metrics required
⚠ Differentiation strategy needs clarification
⚠ Customer testimonials would strengthen claims
⚠ Market positioning could be more precise

Market Fit Analysis:
The {business.get('industry_category', 'industry')} sector shows positive growth trends. Success will depend on execution of their value proposition and ability to demonstrate measurable results.

Recommendation: Strong potential if they can substantiate claims with concrete evidence and develop clear competitive differentiation."""
            
            self._add_message(conversation_id, "Neutral Evaluator", content)
            
            # Mark conversation as completed
            conv["state"] = ConversationState.COMPLETED
        
        # Advance to next round
        if round_num < 4:
            conv["current_round"] += 1
    
    def _add_message(self, conversation_id: str, agent_name: str, content: str):
        """Add a message to the conversation"""
        message = ConversationMessage(
            id=str(uuid.uuid4()),
            agent_name=agent_name,
            content=content,
            timestamp=datetime.now(),
            conversation_id=conversation_id,
            business_id=self.active_conversations[conversation_id]["business_data"].get("business_type_id", "unknown")
        )
        
        if conversation_id not in self.conversation_history:
            self.conversation_history[conversation_id] = []
        
        self.conversation_history[conversation_id].append(message)
        
        # Continue conversation if not completed
        conv = self.active_conversations[conversation_id]
        if conv["state"] == ConversationState.RUNNING and conv["current_round"] <= 4:
            # Add small delay then generate next message
            import threading
            import time
            
            def delayed_next():
                time.sleep(2)  # 2 second delay between messages
                if conv["state"] == ConversationState.RUNNING:
                    self._generate_next_message(conversation_id)
            
            thread = threading.Thread(target=delayed_next)
            thread.daemon = True
            thread.start()
    
    def pause_conversation(self, conversation_id: str) -> bool:
        """Pause conversation with context preservation"""
        if conversation_id in self.active_conversations:
            self.active_conversations[conversation_id]["state"] = ConversationState.PAUSED
            return True
        return False
    
    def resume_conversation(self, conversation_id: str) -> bool:
        """Resume paused conversation"""
        if conversation_id in self.active_conversations:
            conv = self.active_conversations[conversation_id]
            if conv["state"] == ConversationState.PAUSED:
                conv["state"] = ConversationState.RUNNING
                # Continue from where we left off
                self._generate_next_message(conversation_id)
                return True
        return False
    
    def stop_conversation(self, conversation_id: str) -> bool:
        """Stop conversation completely"""
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
            "business_id": conv["business_data"].get("business_type_id", "unknown"),
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
        from models.user_simple import BusinessType
        business = BusinessType.query.filter_by(business_type_id=business_id).first()
        
        if not business:
            return jsonify({"error": "Business not found"}), 404
        
        # Convert business to dict for AI processing
        business_data = {
            "business_type_id": business.business_type_id,
            "name": business.name,
            "description": business.description,
            "industry_category": business.industry_category,
            "created_at": business.created_at.isoformat() if business.created_at else None
        }
        
        # Start the conversation
        conversation_id = conversation_engine.start_conversation(business_data)
        
        return jsonify({
            "conversation_id": conversation_id,
            "status": "started",
            "message": "AI-to-AI conversation initiated",
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

@ai_conversations_bp.route('/<conversation_id>/reset', methods=['POST'])
def reset_conversation(conversation_id):
    """Reset conversation to start fresh"""
    if conversation_id in conversation_engine.active_conversations:
        business_data = conversation_engine.active_conversations[conversation_id]["business_data"]
        conversation_engine.stop_conversation(conversation_id)
        new_conversation_id = conversation_engine.start_conversation(business_data)
        return jsonify({"success": True, "new_conversation_id": new_conversation_id})
    return jsonify({"success": False, "error": "Conversation not found"})

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
    for conv_id, conv in conversation_engine.active_conversations.items():
        if conv["state"] != ConversationState.STOPPED:
            active.append({
                "conversation_id": conv_id,
                "business_name": conv["business_data"].get("name", "Unknown"),
                "state": conv["state"].value,
                "created_at": conv["created_at"].isoformat()
            })
    return jsonify({"active_conversations": active})

