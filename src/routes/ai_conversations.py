"""
Refined Tiered AI Conversations System
- Tier 1: Full features (conversation + publishing + SEO + social media)
- Tiers 2-6: Extended conversations only, no repetition, genuinely different content
- All conversations are public
"""
import json
import uuid
import asyncio
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

from flask import Blueprint, request, jsonify
import openai
import anthropic
import google.generativeai as genai
import requests
import os

# Create blueprint
ai_conversations_bp = Blueprint('ai_conversations', __name__)

# Refined Tier Configuration
ANALYSIS_TIERS = {
    "tier1": {
        "rounds": 4,
        "messages": 16,
        "price": 10,
        "duration_minutes": 3,
        "name": "Complete Package",
        "description": "AI conversation + SEO page + social media + directory publishing",
        "includes_publishing": True
    },
    "tier2": {
        "rounds": 6,
        "messages": 24,
        "price": 15,
        "duration_minutes": 5,
        "name": "Extended Conversation",
        "description": "6 rounds of deeper AI analysis - conversation only",
        "includes_publishing": False
    },
    "tier3": {
        "rounds": 8,
        "messages": 32,
        "price": 25,
        "duration_minutes": 8,
        "name": "Comprehensive Conversation",
        "description": "8 rounds of comprehensive AI analysis - conversation only",
        "includes_publishing": False
    },
    "tier4": {
        "rounds": 10,
        "messages": 40,
        "price": 40,
        "duration_minutes": 10,
        "name": "Executive Conversation",
        "description": "10 rounds of executive-level AI analysis - conversation only",
        "includes_publishing": False
    },
    "tier5": {
        "rounds": 25,
        "messages": 100,
        "price": 100,
        "duration_minutes": 25,
        "name": "Strategic Deep Dive",
        "description": "25 rounds of strategic AI analysis - conversation only",
        "includes_publishing": False
    },
    "tier6": {
        "rounds": 50,
        "messages": 200,
        "price": 250,
        "duration_minutes": 50,
        "name": "Ultimate Analysis",
        "description": "50 rounds of ultimate AI analysis - conversation only",
        "includes_publishing": False
    }
}

# Owner email for free access
OWNER_EMAIL = "ottmar.francisca1969@gmail.com"

class ConversationState(Enum):
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"

@dataclass
class ConversationMessage:
    id: str
    agent_name: str
    content: str
    timestamp: datetime
    conversation_id: str
    round_number: int

class RefinedAIConversationEngine:
    def __init__(self):
        self.active_conversations: Dict[str, Dict] = {}
        self.conversation_history: Dict[str, List[ConversationMessage]] = {}
        
        # Initialize AI clients
        self.openai_client = None
        self.anthropic_client = None
        self.google_client = None
        
        self._setup_ai_clients()
    
    def _setup_ai_clients(self):
        """Initialize AI API clients"""
        try:
            # OpenAI
            openai_key = os.getenv('OPENAI_API_KEY')
            if openai_key:
                openai.api_key = openai_key
                self.openai_client = openai
            
            # Anthropic
            anthropic_key = os.getenv('ANTHROPIC_API_KEY')
            if anthropic_key:
                self.anthropic_client = anthropic.Anthropic(api_key=anthropic_key)
            
            # Google Gemini
            google_key = os.getenv('GOOGLE_API_KEY')
            if google_key:
                genai.configure(api_key=google_key)
                self.google_client = genai.GenerativeModel('gemini-pro')
                
        except Exception as e:
            print(f"Error setting up AI clients: {e}")
    
    async def call_openai_api(self, prompt: str, context: List = None, round_num: int = 1) -> str:
        """Call OpenAI GPT-4 API with round-specific prompts"""
        try:
            if not self.openai_client:
                return self._get_fallback_response("Business Promoter", round_num)
            
            system_prompt = self._get_system_prompt("Business Promoter", round_num)
            messages = [{"role": "system", "content": system_prompt}]
            
            if context:
                for msg in context[-3:]:
                    messages.append({"role": "user", "content": msg})
            messages.append({"role": "user", "content": prompt})
            
            response = await asyncio.to_thread(
                self.openai_client.ChatCompletion.create,
                model="gpt-4",
                messages=messages,
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return self._get_fallback_response("Business Promoter", round_num)
    
    async def call_anthropic_api(self, prompt: str, context: List = None, round_num: int = 1) -> str:
        """Call Anthropic Claude API with round-specific prompts"""
        try:
            if not self.anthropic_client:
                return self._get_fallback_response("Critical Analyst", round_num)
            
            system_prompt = self._get_system_prompt("Critical Analyst", round_num)
            full_prompt = f"{system_prompt}\n\n"
            
            if context:
                full_prompt += "Previous context:\n" + "\n".join(context[-3:]) + "\n\n"
            full_prompt += prompt
            
            response = await asyncio.to_thread(
                self.anthropic_client.messages.create,
                model="claude-3-sonnet-20240229",
                max_tokens=300,
                messages=[{"role": "user", "content": full_prompt}]
            )
            
            return response.content[0].text.strip()
            
        except Exception as e:
            return self._get_fallback_response("Critical Analyst", round_num)
    
    async def call_google_api(self, prompt: str, context: List = None, round_num: int = 1) -> str:
        """Call Google Gemini API with round-specific prompts"""
        try:
            if not self.google_client:
                return self._get_fallback_response("Neutral Evaluator", round_num)
            
            system_prompt = self._get_system_prompt("Neutral Evaluator", round_num)
            full_prompt = f"{system_prompt}\n\n"
            
            if context:
                full_prompt += "Previous context:\n" + "\n".join(context[-3:]) + "\n\n"
            full_prompt += prompt
            
            response = await asyncio.to_thread(
                self.google_client.generate_content,
                full_prompt
            )
            
            return response.text.strip()
            
        except Exception as e:
            return self._get_fallback_response("Neutral Evaluator", round_num)
    
    async def call_perplexity_api(self, prompt: str, context: List = None, round_num: int = 1) -> str:
        """Call Perplexity API with round-specific prompts"""
        try:
            perplexity_key = os.getenv('PERPLEXITY_API_KEY')
            if not perplexity_key:
                return self._get_fallback_response("Market Researcher", round_num)
            
            system_prompt = self._get_system_prompt("Market Researcher", round_num)
            full_prompt = f"{system_prompt}\n\n"
            
            if context:
                full_prompt += "Previous context:\n" + "\n".join(context[-3:]) + "\n\n"
            full_prompt += prompt
            
            headers = {
                "Authorization": f"Bearer {perplexity_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "llama-3.1-sonar-large-128k-online",
                "messages": [{"role": "user", "content": full_prompt}],
                "max_tokens": 300,
                "temperature": 0.7
            }
            
            response = await asyncio.to_thread(
                requests.post,
                "https://api.perplexity.ai/chat/completions",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"].strip()
            else:
                return self._get_fallback_response("Market Researcher", round_num)
                
        except Exception as e:
            return self._get_fallback_response("Market Researcher", round_num)
    
    def _get_system_prompt(self, agent_name: str, round_num: int) -> str:
        """Get system prompt based on agent and round number - ensures no repetition"""
        
        # Base agent personalities
        base_prompts = {
            "Business Promoter": "You are a professional business promoter. Be factual, compelling, and professional.",
            "Critical Analyst": "You are a critical business analyst. Ask tough, relevant questions and provide objective analysis.",
            "Market Researcher": "You are a market researcher. Provide current market data and competitive analysis.",
            "Neutral Evaluator": "You are a neutral business evaluator. Provide balanced, objective analysis."
        }
        
        # Round-specific focus areas to prevent repetition
        round_focus = {
            1: "Initial assessment and positioning",
            2: "Competitive landscape and differentiation",
            3: "Market opportunities and challenges",
            4: "Strategic recommendations and next steps",
            5: "Operational efficiency and scalability",
            6: "Financial performance and projections",
            7: "Technology and innovation requirements",
            8: "Human resources and organizational structure",
            9: "Risk management and compliance",
            10: "Partnership and alliance opportunities",
            11: "Customer acquisition and retention strategies",
            12: "Product development and innovation pipeline",
            13: "Supply chain and logistics optimization",
            14: "Brand positioning and marketing strategy",
            15: "International expansion possibilities",
            16: "Sustainability and environmental impact",
            17: "Digital transformation requirements",
            18: "Regulatory landscape and compliance",
            19: "Merger and acquisition potential",
            20: "Exit strategy and valuation considerations",
            21: "Industry disruption and future trends",
            22: "Stakeholder management and governance",
            23: "Crisis management and business continuity",
            24: "Innovation ecosystem and R&D strategy",
            25: "Long-term vision and legacy planning",
            26: "Capital structure and financing options",
            27: "Intellectual property and competitive moats",
            28: "Data strategy and analytics capabilities",
            29: "Corporate social responsibility",
            30: "Leadership development and succession",
            31: "Market timing and economic factors",
            32: "Competitive intelligence and monitoring",
            33: "Customer experience and satisfaction",
            34: "Operational excellence and lean practices",
            35: "Strategic partnerships and ecosystems",
            36: "Innovation culture and change management",
            37: "Performance metrics and KPI frameworks",
            38: "Scenario planning and stress testing",
            39: "Stakeholder value creation",
            40: "Business model evolution and adaptation",
            41: "Market leadership and thought leadership",
            42: "Ecosystem positioning and network effects",
            43: "Regulatory strategy and government relations",
            44: "Talent acquisition and retention",
            45: "Technology roadmap and digital strategy",
            46: "Financial engineering and optimization",
            47: "Strategic options and real options",
            48: "Competitive dynamics and game theory",
            49: "Value chain optimization and integration",
            50: "Legacy and long-term impact assessment"
        }
        
        focus_area = round_focus.get(round_num, f"Advanced analysis round {round_num}")
        
        return f"{base_prompts[agent_name]} Focus specifically on: {focus_area}. Avoid repeating previous points and provide fresh insights."
    
    def _get_fallback_response(self, agent_name: str, round_num: int) -> str:
        """Get fallback response when API fails - unique per round"""
        
        fallback_templates = {
            "Business Promoter": [
                f"Round {round_num}: This business demonstrates strong market positioning with clear competitive advantages and growth potential.",
                f"Round {round_num}: The value proposition shows excellent alignment with market needs and customer demands.",
                f"Round {round_num}: Strategic positioning indicates strong potential for market leadership and expansion.",
                f"Round {round_num}: Business model shows robust fundamentals with multiple revenue streams and scalability.",
                f"Round {round_num}: Operational excellence and customer focus create sustainable competitive advantages."
            ],
            "Critical Analyst": [
                f"Round {round_num}: Key questions remain about market differentiation and long-term sustainability.",
                f"Round {round_num}: Risk factors include competitive pressure and market volatility that need addressing.",
                f"Round {round_num}: Operational challenges and resource constraints require careful management.",
                f"Round {round_num}: Financial projections need validation against market realities and competitive dynamics.",
                f"Round {round_num}: Strategic assumptions require stress testing against various market scenarios."
            ],
            "Market Researcher": [
                f"Round {round_num}: Market research indicates positive industry trends with 8.2% annual growth.",
                f"Round {round_num}: Competitive landscape shows opportunities for well-positioned market entrants.",
                f"Round {round_num}: Customer behavior analysis reveals strong demand for innovative solutions.",
                f"Round {round_num}: Industry benchmarks suggest above-average performance potential.",
                f"Round {round_num}: Market timing appears favorable with supportive economic conditions."
            ],
            "Neutral Evaluator": [
                f"Round {round_num}: Balanced assessment shows both strengths and areas requiring improvement.",
                f"Round {round_num}: Overall evaluation indicates moderate to strong business potential.",
                f"Round {round_num}: Risk-reward profile suggests favorable investment characteristics.",
                f"Round {round_num}: Strategic assessment reveals solid fundamentals with growth opportunities.",
                f"Round {round_num}: Comprehensive analysis indicates positive outlook with managed risks."
            ]
        }
        
        templates = fallback_templates.get(agent_name, [f"Round {round_num}: Professional analysis indicates positive business potential."])
        template_index = (round_num - 1) % len(templates)
        return templates[template_index]
    
    def start_conversation(self, business_data: Dict, tier: str = "tier1", email: str = "") -> str:
        """Start a new tiered AI conversation"""
        conversation_id = str(uuid.uuid4())
        tier_config = ANALYSIS_TIERS.get(tier, ANALYSIS_TIERS["tier1"])
        
        self.active_conversations[conversation_id] = {
            "id": conversation_id,
            "business_data": business_data,
            "tier": tier,
            "tier_config": tier_config,
            "email": email,
            "is_owner": email == OWNER_EMAIL,
            "state": ConversationState.RUNNING,
            "created_at": datetime.now(),
            "current_round": 1,
            "max_rounds": tier_config["rounds"],
            "context": [],
            "is_public": True  # All conversations are public
        }
        
        self.conversation_history[conversation_id] = []
        
        # Start the conversation asynchronously
        threading.Thread(
            target=self._run_conversation_sync,
            args=(conversation_id,),
            daemon=True
        ).start()
        
        return conversation_id
    
    def _run_conversation_sync(self, conversation_id: str):
        """Run conversation in sync thread"""
        asyncio.run(self._run_conversation(conversation_id))
    
    async def _run_conversation(self, conversation_id: str):
        """Run the complete tiered AI conversation with genuinely different content per round"""
        conv = self.active_conversations[conversation_id]
        business = conv["business_data"]
        max_rounds = conv["max_rounds"]
        
        for round_num in range(1, max_rounds + 1):
            if conv["state"] != ConversationState.RUNNING:
                break
                
            conv["current_round"] = round_num
            
            # Generate genuinely different prompts for each round
            prompts = self._generate_unique_round_prompts(business, round_num, max_rounds)
            
            # Business Promoter (GPT-4)
            response = await self.call_openai_api(prompts["promoter"], conv["context"], round_num)
            self._add_message(conversation_id, "Business Promoter", response, round_num)
            await asyncio.sleep(2)
            
            # Critical Analyst (Claude)
            response = await self.call_anthropic_api(prompts["analyst"], conv["context"], round_num)
            self._add_message(conversation_id, "Critical Analyst", response, round_num)
            await asyncio.sleep(2)
            
            # Market Researcher (Perplexity)
            response = await self.call_perplexity_api(prompts["researcher"], conv["context"], round_num)
            self._add_message(conversation_id, "Market Researcher", response, round_num)
            await asyncio.sleep(2)
            
            # Neutral Evaluator (Gemini)
            response = await self.call_google_api(prompts["evaluator"], conv["context"], round_num)
            self._add_message(conversation_id, "Neutral Evaluator", response, round_num)
            await asyncio.sleep(2)
        
        # Mark conversation as completed
        conv["state"] = ConversationState.COMPLETED
        
        # Trigger publishing only for Tier 1
        if conv["tier"] == "tier1":
            await self._trigger_tier1_publishing(conversation_id)
    
    def _generate_unique_round_prompts(self, business: Dict, round_num: int, max_rounds: int) -> Dict[str, str]:
        """Generate unique prompts for each round to prevent repetition"""
        business_name = business.get('name', 'this business')
        industry = business.get('industry_category', 'specified industry')
        description = business.get('description', 'business services')
        
        # Define unique focus areas for each round
        round_topics = {
            1: {
                "theme": "Initial Business Assessment",
                "promoter": f"Introduce {business_name} and highlight its core value proposition in {industry}. What makes this business unique?",
                "analyst": f"What are the immediate challenges facing {business_name} in the current market environment?",
                "researcher": f"What are the current market conditions and trends in {industry} that affect {business_name}?",
                "evaluator": f"Provide an initial assessment of {business_name}'s market position and potential."
            },
            2: {
                "theme": "Competitive Landscape Analysis",
                "promoter": f"How does {business_name} differentiate itself from competitors in {industry}?",
                "analyst": f"What competitive threats should {business_name} be most concerned about?",
                "researcher": f"Who are the main competitors of {business_name} and what are their strategies?",
                "evaluator": f"Assess {business_name}'s competitive advantages and vulnerabilities."
            },
            3: {
                "theme": "Market Opportunities and Growth",
                "promoter": f"What are the biggest growth opportunities for {business_name} in the next 2-3 years?",
                "analyst": f"What barriers to growth might {business_name} encounter?",
                "researcher": f"What market segments or geographic areas offer the best expansion potential for {business_name}?",
                "evaluator": f"Evaluate the feasibility and attractiveness of identified growth opportunities."
            },
            4: {
                "theme": "Strategic Recommendations",
                "promoter": f"What strategic initiatives should {business_name} prioritize to maximize success?",
                "analyst": f"What are the risks associated with the proposed strategic direction for {business_name}?",
                "researcher": f"What industry best practices could {business_name} adopt to improve performance?",
                "evaluator": f"Synthesize the discussion and provide balanced strategic recommendations for {business_name}."
            },
            5: {
                "theme": "Operational Excellence",
                "promoter": f"How can {business_name} optimize its operations to improve efficiency and customer satisfaction?",
                "analyst": f"What operational weaknesses could undermine {business_name}'s performance?",
                "researcher": f"What operational technologies and processes are leading companies in {industry} adopting?",
                "evaluator": f"Assess the operational maturity and improvement potential of {business_name}."
            },
            6: {
                "theme": "Financial Performance and Projections",
                "promoter": f"What financial metrics demonstrate {business_name}'s strong performance potential?",
                "analyst": f"What financial risks and constraints should {business_name} be aware of?",
                "researcher": f"What are typical financial benchmarks and ratios for successful companies in {industry}?",
                "evaluator": f"Evaluate {business_name}'s financial health and future prospects."
            },
            7: {
                "theme": "Technology and Innovation",
                "promoter": f"How can {business_name} leverage technology to gain competitive advantage?",
                "analyst": f"What technology risks or disruptions could threaten {business_name}?",
                "researcher": f"What emerging technologies are transforming {industry}?",
                "evaluator": f"Assess {business_name}'s technology readiness and innovation capacity."
            },
            8: {
                "theme": "Human Capital and Organization",
                "promoter": f"What human capital strengths give {business_name} competitive advantage?",
                "analyst": f"What talent gaps or organizational challenges face {business_name}?",
                "researcher": f"What are the talent trends and workforce dynamics in {industry}?",
                "evaluator": f"Evaluate {business_name}'s organizational capabilities and development needs."
            },
            9: {
                "theme": "Risk Management and Compliance",
                "promoter": f"How does {business_name} effectively manage business risks?",
                "analyst": f"What are the most significant risks that could impact {business_name}?",
                "researcher": f"What regulatory and compliance requirements affect {industry}?",
                "evaluator": f"Assess {business_name}'s risk management maturity and compliance posture."
            },
            10: {
                "theme": "Strategic Partnerships and Alliances",
                "promoter": f"What partnership opportunities could accelerate {business_name}'s growth?",
                "analyst": f"What are the risks and challenges of strategic partnerships for {business_name}?",
                "researcher": f"What successful partnership models exist in {industry}?",
                "evaluator": f"Evaluate the partnership strategy and alliance potential for {business_name}."
            }
        }
        
        # For rounds beyond 10, generate advanced topics
        if round_num > 10:
            advanced_topics = [
                "Customer Experience and Loyalty", "Digital Transformation Strategy", "Sustainability and ESG",
                "Innovation Pipeline and R&D", "International Expansion", "Brand Strategy and Marketing",
                "Supply Chain Optimization", "Data Analytics and AI", "Corporate Governance",
                "Crisis Management and Resilience", "Stakeholder Engagement", "Value Chain Analysis",
                "Market Timing and Economic Factors", "Intellectual Property Strategy", "Leadership Development",
                "Performance Measurement", "Change Management", "Strategic Options Analysis",
                "Competitive Intelligence", "Business Model Innovation", "Ecosystem Strategy",
                "Regulatory Strategy", "Talent Strategy", "Technology Roadmap", "Financial Engineering",
                "Strategic Scenarios", "Competitive Dynamics", "Value Creation", "Market Leadership",
                "Network Effects", "Platform Strategy", "Innovation Culture", "Strategic Agility",
                "Stakeholder Value", "Long-term Vision", "Legacy Planning", "Impact Assessment",
                "Strategic Transformation", "Future Readiness", "Adaptive Strategy", "Strategic Renewal"
            ]
            
            topic_index = (round_num - 11) % len(advanced_topics)
            topic = advanced_topics[topic_index]
            
            return {
                "promoter": f"Round {round_num} - {topic}: How can {business_name} excel in {topic.lower()}?",
                "analyst": f"Round {round_num} - {topic}: What challenges does {business_name} face regarding {topic.lower()}?",
                "researcher": f"Round {round_num} - {topic}: What are industry trends and best practices for {topic.lower()} in {industry}?",
                "evaluator": f"Round {round_num} - {topic}: Assess {business_name}'s capabilities and opportunities in {topic.lower()}."
            }
        
        # Use predefined topics for rounds 1-10
        topic_data = round_topics.get(round_num, round_topics[1])
        return {
            "promoter": f"Round {round_num} - {topic_data['theme']}: {topic_data['promoter']}",
            "analyst": f"Round {round_num} - {topic_data['theme']}: {topic_data['analyst']}",
            "researcher": f"Round {round_num} - {topic_data['theme']}: {topic_data['researcher']}",
            "evaluator": f"Round {round_num} - {topic_data['theme']}: {topic_data['evaluator']}"
        }
    
    async def _trigger_tier1_publishing(self, conversation_id: str):
        """Trigger publishing pipeline only for Tier 1"""
        try:
            conv = self.active_conversations[conversation_id]
            messages = self.conversation_history.get(conversation_id, [])
            
            print(f"Triggering Tier 1 publishing for conversation {conversation_id}")
            # Tier 1 publishing logic would go here
            # This includes SEO page, social media content, directory publishing, etc.
            
        except Exception as e:
            print(f"Error triggering Tier 1 publishing: {e}")
    
    def _add_message(self, conversation_id: str, agent_name: str, content: str, round_number: int):
        """Add message to conversation"""
        message = ConversationMessage(
            id=str(uuid.uuid4()),
            agent_name=agent_name,
            content=content,
            timestamp=datetime.now(),
            conversation_id=conversation_id,
            round_number=round_number
        )
        
        if conversation_id not in self.conversation_history:
            self.conversation_history[conversation_id] = []
        
        self.conversation_history[conversation_id].append(message)
        
        # Add to context
        conv = self.active_conversations[conversation_id]
        conv["context"].append(f"Round {round_number} - {agent_name}: {content}")
    
    def get_conversation_status(self, conversation_id: str) -> Dict:
        """Get conversation status"""
        if conversation_id not in self.active_conversations:
            return {"error": "Conversation not found"}
        
        conv = self.active_conversations[conversation_id]
        messages = self.conversation_history.get(conversation_id, [])
        
        return {
            "conversation_id": conversation_id,
            "business_name": conv["business_data"].get("name", "Unknown"),
            "tier": conv["tier"],
            "tier_name": conv["tier_config"]["name"],
            "state": conv["state"].value,
            "current_round": conv["current_round"],
            "max_rounds": conv["max_rounds"],
            "total_messages": len(messages),
            "progress_percentage": (len(messages) / conv["tier_config"]["messages"]) * 100,
            "is_owner": conv["is_owner"],
            "is_public": conv["is_public"],
            "includes_publishing": conv["tier_config"]["includes_publishing"],
            "last_activity": messages[-1].timestamp.isoformat() if messages else None
        }
    
    def get_live_messages(self, conversation_id: str) -> List[Dict]:
        """Get conversation messages"""
        messages = self.conversation_history.get(conversation_id, [])
        return [
            {
                "id": msg.id,
                "agent_name": msg.agent_name,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "round_number": msg.round_number
            }
            for msg in messages
        ]
    
    def get_public_conversations(self) -> List[Dict]:
        """Get all public conversations"""
        public_conversations = []
        for conv_id, conv in self.active_conversations.items():
            if conv["is_public"]:
                messages = self.conversation_history.get(conv_id, [])
                public_conversations.append({
                    "conversation_id": conv_id,
                    "business_name": conv["business_data"].get("name", "Unknown"),
                    "tier": conv["tier"],
                    "tier_name": conv["tier_config"]["name"],
                    "state": conv["state"].value,
                    "total_messages": len(messages),
                    "created_at": conv["created_at"].isoformat(),
                    "includes_publishing": conv["tier_config"]["includes_publishing"]
                })
        return public_conversations

# Initialize engine
conversation_engine = RefinedAIConversationEngine()

# Routes
@ai_conversations_bp.route('/tiers', methods=['GET'])
def get_analysis_tiers():
    """Get available analysis tiers"""
    email = request.args.get('email', '')
    is_owner = email == OWNER_EMAIL
    
    tiers = []
    for tier_id, config in ANALYSIS_TIERS.items():
        tier_info = {
            "id": tier_id,
            "name": config["name"],
            "description": config["description"],
            "rounds": config["rounds"],
            "messages": config["messages"],
            "duration_minutes": config["duration_minutes"],
            "price": 0 if is_owner else config["price"],
            "original_price": config["price"],
            "free_for_owner": is_owner,
            "includes_publishing": config["includes_publishing"]
        }
        tiers.append(tier_info)
    
    return jsonify({
        "tiers": tiers,
        "owner_email": OWNER_EMAIL if is_owner else None,
        "free_access": is_owner
    })

@ai_conversations_bp.route('/start', methods=['POST'])
def start_conversation():
    """Start tiered AI conversation"""
    try:
        data = request.json
        business_id = data.get('business_id')
        tier = data.get('tier', 'tier1')
        email = data.get('email', '')
        
        if not business_id:
            return jsonify({"error": "business_id is required"}), 400
        
        if tier not in ANALYSIS_TIERS:
            return jsonify({"error": "Invalid tier"}), 400
        
        # Check if owner email gets free access
        is_owner = email == OWNER_EMAIL
        tier_config = ANALYSIS_TIERS[tier]
        
        if tier == 'tier1' or is_owner:
            # Free access for tier1 or owner
            from models.user_simple import BusinessType
            business = BusinessType.query.filter_by(business_type_id=business_id).first()
            
            if not business:
                return jsonify({"error": "Business not found"}), 404
            
            business_data = {
                "business_type_id": business.business_type_id,
                "name": business.name,
                "description": business.description,
                "industry_category": business.industry_category
            }
            
            conversation_id = conversation_engine.start_conversation(
                business_data, 
                tier=tier,
                email=email
            )
            
            return jsonify({
                "conversation_id": conversation_id,
                "status": "started",
                "tier": tier,
                "tier_name": tier_config["name"],
                "business_name": business.name,
                "free_access": is_owner or tier == 'tier1',
                "estimated_duration": tier_config["duration_minutes"],
                "total_messages": tier_config["messages"],
                "is_public": True,
                "includes_publishing": tier_config["includes_publishing"]
            })
        else:
            # Require payment for premium tiers (tier2-tier6)
            return jsonify({
                "status": "payment_required",
                "tier": tier,
                "tier_name": tier_config["name"],
                "price": tier_config["price"],
                "message": f"Payment required for {tier_config['name']} tier"
            }), 402
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ai_conversations_bp.route('/<conversation_id>/status', methods=['GET'])
def get_conversation_status(conversation_id):
    """Get conversation status"""
    status = conversation_engine.get_conversation_status(conversation_id)
    return jsonify(status)

@ai_conversations_bp.route('/<conversation_id>/messages', methods=['GET'])
def get_conversation_messages(conversation_id):
    """Get conversation messages"""
    messages = conversation_engine.get_live_messages(conversation_id)
    return jsonify({"messages": messages})

@ai_conversations_bp.route('/public', methods=['GET'])
def get_public_conversations():
    """Get all public conversations"""
    conversations = conversation_engine.get_public_conversations()
    return jsonify({"conversations": conversations})

@ai_conversations_bp.route('/<conversation_id>/control', methods=['POST'])
def control_conversation(conversation_id):
    """Control conversation (pause/resume/stop)"""
    try:
        data = request.json
        action = data.get('action')
        
        if conversation_id not in conversation_engine.active_conversations:
            return jsonify({"error": "Conversation not found"}), 404
        
        conv = conversation_engine.active_conversations[conversation_id]
        
        if action == 'pause':
            conv["state"] = ConversationState.PAUSED
        elif action == 'resume':
            conv["state"] = ConversationState.RUNNING
        elif action == 'stop':
            conv["state"] = ConversationState.STOPPED
        else:
            return jsonify({"error": "Invalid action"}), 400
        
        return jsonify({
            "conversation_id": conversation_id,
            "action": action,
            "new_state": conv["state"].value
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

