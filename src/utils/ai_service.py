import openai
import requests
import json
import random
from datetime import datetime
from flask import current_app

class AIService:
    """Enhanced AI service for generating contextual persuasion responses."""
    
    def __init__(self):
        self.openai_api_key = current_app.config.get('OPENAI_API_KEY')
        self.anthropic_api_key = current_app.config.get('ANTHROPIC_API_KEY')
        
        # Initialize OpenAI if API key is available
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
    
    def generate_persuasion_responses(self, business_type, target_audience, mission_objective):
        """Generate AI-powered persuasion responses for different agent types."""
        
        # Create context for AI generation
        business_context = self._build_business_context(business_type)
        audience_context = self._build_audience_context(target_audience)
        
        # Generate responses for each agent type
        responses = {
            'logic_agent': self._generate_logic_response(business_context, audience_context, mission_objective),
            'emotion_agent': self._generate_emotion_response(business_context, audience_context, mission_objective),
            'creative_agent': self._generate_creative_response(business_context, audience_context, mission_objective),
            'authority_agent': self._generate_authority_response(business_context, audience_context, mission_objective),
            'social_proof_agent': self._generate_social_proof_response(business_context, audience_context, mission_objective)
        }
        
        return responses
    
    def _build_business_context(self, business_type):
        """Build context string for business type."""
        if not business_type:
            return "general business"
        
        context = f"Business: {business_type.get('name', 'Unknown Business')}"
        if business_type.get('description'):
            context += f"\nDescription: {business_type['description']}"
        if business_type.get('industry_category'):
            context += f"\nIndustry: {business_type['industry_category']}"
        
        return context
    
    def _build_audience_context(self, target_audience):
        """Build context string for target audience."""
        if not target_audience:
            return "general audience"
        
        context = f"Target Audience: {target_audience.get('name', 'Unnamed Audience')}"
        
        # Handle manual description
        if target_audience.get('psychographics', {}).get('manual_description'):
            context += f"\nAudience Profile: {target_audience['psychographics']['manual_description']}"
        elif target_audience.get('description'):
            context += f"\nDescription: {target_audience['description']}"
        
        # Add demographic info if available
        demographics = target_audience.get('demographics', {})
        if demographics:
            demo_parts = []
            for key, value in demographics.items():
                if value:
                    demo_parts.append(f"{key}: {value}")
            if demo_parts:
                context += f"\nDemographics: {', '.join(demo_parts)}"
        
        return context
    
    def _generate_logic_response(self, business_context, audience_context, mission_objective):
        """Generate logic-based persuasion response."""
        
        if self.openai_api_key:
            try:
                return self._generate_openai_response(
                    agent_type="Logic Agent",
                    business_context=business_context,
                    audience_context=audience_context,
                    mission_objective=mission_objective,
                    focus="logical reasoning, facts, data, and rational benefits"
                )
            except Exception as e:
                print(f"OpenAI API error: {e}")
        
        # Fallback to template-based generation
        return self._generate_template_logic_response(business_context, audience_context, mission_objective)
    
    def _generate_emotion_response(self, business_context, audience_context, mission_objective):
        """Generate emotion-based persuasion response."""
        
        if self.openai_api_key:
            try:
                return self._generate_openai_response(
                    agent_type="Emotion Agent",
                    business_context=business_context,
                    audience_context=audience_context,
                    mission_objective=mission_objective,
                    focus="emotional appeal, feelings, desires, fears, and aspirations"
                )
            except Exception as e:
                print(f"OpenAI API error: {e}")
        
        # Fallback to template-based generation
        return self._generate_template_emotion_response(business_context, audience_context, mission_objective)
    
    def _generate_creative_response(self, business_context, audience_context, mission_objective):
        """Generate creative persuasion response."""
        
        if self.openai_api_key:
            try:
                return self._generate_openai_response(
                    agent_type="Creative Agent",
                    business_context=business_context,
                    audience_context=audience_context,
                    mission_objective=mission_objective,
                    focus="creative storytelling, metaphors, vivid imagery, and unique angles"
                )
            except Exception as e:
                print(f"OpenAI API error: {e}")
        
        # Fallback to template-based generation
        return self._generate_template_creative_response(business_context, audience_context, mission_objective)
    
    def _generate_authority_response(self, business_context, audience_context, mission_objective):
        """Generate authority-based persuasion response."""
        
        if self.openai_api_key:
            try:
                return self._generate_openai_response(
                    agent_type="Authority Agent",
                    business_context=business_context,
                    audience_context=audience_context,
                    mission_objective=mission_objective,
                    focus="expertise, credentials, industry leadership, and professional authority"
                )
            except Exception as e:
                print(f"OpenAI API error: {e}")
        
        # Fallback to template-based generation
        return self._generate_template_authority_response(business_context, audience_context, mission_objective)
    
    def _generate_social_proof_response(self, business_context, audience_context, mission_objective):
        """Generate social proof-based persuasion response."""
        
        if self.openai_api_key:
            try:
                return self._generate_openai_response(
                    agent_type="Social Proof Agent",
                    business_context=business_context,
                    audience_context=audience_context,
                    mission_objective=mission_objective,
                    focus="testimonials, reviews, case studies, popularity, and peer validation"
                )
            except Exception as e:
                print(f"OpenAI API error: {e}")
        
        # Fallback to template-based generation
        return self._generate_template_social_proof_response(business_context, audience_context, mission_objective)
    
    def _generate_openai_response(self, agent_type, business_context, audience_context, mission_objective, focus):
        """Generate response using OpenAI API."""
        
        prompt = f"""You are a {agent_type} in a cognitive persuasion system. Your role is to create compelling messages focused on {focus}.

{business_context}

{audience_context}

Mission Objective: {mission_objective}

Generate a persuasive message that:
1. Is specifically tailored to the business and audience
2. Focuses on {focus}
3. Is compelling and actionable
4. Is approximately 1-2 sentences long
5. Directly relates to the mission objective

Response:"""

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"You are a {agent_type} specializing in {focus}. Create concise, compelling persuasive messages."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"OpenAI API call failed: {e}")
            raise e
    
    def _generate_template_logic_response(self, business_context, audience_context, mission_objective):
        """Generate logic-based response using templates."""
        
        business_name = self._extract_business_name(business_context)
        industry = self._extract_industry(business_context)
        
        templates = [
            f"Our {business_name} follows strict industry standards and proven methodologies to deliver measurable results for your {mission_objective.lower()}.",
            f"With documented processes and quality assurance protocols, {business_name} provides reliable, consistent outcomes that you can depend on.",
            f"The data shows that our systematic approach to {industry.lower()} delivers superior performance compared to traditional methods.",
            f"Our certified processes and industry compliance ensure that your investment in {business_name} delivers quantifiable value.",
            f"Evidence-based strategies and proven track record make {business_name} the logical choice for achieving your {mission_objective.lower()}."
        ]
        
        return random.choice(templates)
    
    def _generate_template_emotion_response(self, business_context, audience_context, mission_objective):
        """Generate emotion-based response using templates."""
        
        business_name = self._extract_business_name(business_context)
        
        templates = [
            f"Imagine the peace of mind knowing that {business_name} will exceed your expectations and protect what matters most to you.",
            f"Feel confident and secure with {business_name} - we understand what's truly important to you and your family.",
            f"Experience the joy and satisfaction that comes from making the right choice with {business_name}.",
            f"Don't let worry and uncertainty hold you back - {business_name} is here to give you the confidence you deserve.",
            f"Transform your concerns into excitement about the future with {business_name} by your side."
        ]
        
        return random.choice(templates)
    
    def _generate_template_creative_response(self, business_context, audience_context, mission_objective):
        """Generate creative response using templates."""
        
        business_name = self._extract_business_name(business_context)
        industry = self._extract_industry(business_context)
        
        templates = [
            f"Like a master craftsman perfecting their art, {business_name} transforms ordinary {industry.lower()} into extraordinary experiences.",
            f"Think of {business_name} as your personal architect of success, designing solutions that perfectly match your vision.",
            f"Just as a lighthouse guides ships safely to shore, {business_name} illuminates the path to your {mission_objective.lower()}.",
            f"Picture {business_name} as the bridge between where you are now and where you want to be - strong, reliable, and beautifully designed.",
            f"Like a symphony conductor bringing harmony to complex music, {business_name} orchestrates every detail of your {mission_objective.lower()}."
        ]
        
        return random.choice(templates)
    
    def _generate_template_authority_response(self, business_context, audience_context, mission_objective):
        """Generate authority-based response using templates."""
        
        business_name = self._extract_business_name(business_context)
        industry = self._extract_industry(business_context)
        
        templates = [
            f"As industry leaders with years of specialized experience, {business_name} sets the standard for excellence in {industry.lower()}.",
            f"Our team of certified professionals at {business_name} brings decades of expertise to every project we undertake.",
            f"Recognized by industry associations and trusted by professionals, {business_name} represents the pinnacle of {industry.lower()} expertise.",
            f"When other businesses need {industry.lower()} solutions, they turn to {business_name} - the authority in our field.",
            f"Our credentials, certifications, and industry recognition make {business_name} the definitive choice for your {mission_objective.lower()}."
        ]
        
        return random.choice(templates)
    
    def _generate_template_social_proof_response(self, business_context, audience_context, mission_objective):
        """Generate social proof response using templates."""
        
        business_name = self._extract_business_name(business_context)
        
        templates = [
            f"Join hundreds of satisfied customers who have already discovered why {business_name} is the preferred choice in our industry.",
            f"Our 5-star reviews and customer testimonials speak volumes about the quality and service you can expect from {business_name}.",
            f"See why leading businesses and discerning customers consistently choose {business_name} for their most important projects.",
            f"With a proven track record of success stories and happy customers, {business_name} has earned its reputation for excellence.",
            f"Don't just take our word for it - our growing community of loyal customers proves that {business_name} delivers on its promises."
        ]
        
        return random.choice(templates)
    
    def _extract_business_name(self, business_context):
        """Extract business name from context."""
        if "Business:" in business_context:
            name = business_context.split("Business:")[1].split("\n")[0].strip()
            return name if name else "our business"
        return "our business"
    
    def _extract_industry(self, business_context):
        """Extract industry from context."""
        if "Industry:" in business_context:
            industry = business_context.split("Industry:")[1].split("\n")[0].strip()
            return industry if industry else "our industry"
        return "our industry"
    
    def calculate_credit_cost(self, session_data):
        """Calculate credit cost for an AI session."""
        base_cost = 1.0  # Base cost per session
        
        # Add cost based on complexity
        if session_data.get('mission_objective'):
            objective_length = len(session_data['mission_objective'])
            if objective_length > 100:
                base_cost += 0.5
        
        # Add cost for custom business types
        if session_data.get('business_type', {}).get('is_custom'):
            base_cost += 0.3
        
        # Add cost for manual audience descriptions
        audience = session_data.get('target_audience', {})
        if audience.get('psychographics', {}).get('manual_description'):
            base_cost += 0.2
        
        return round(base_cost, 2)
    
    def is_configured(self):
        """Check if AI service is properly configured."""
        return bool(self.openai_api_key or self.anthropic_api_key)
    
    def get_available_models(self):
        """Get list of available AI models."""
        models = []
        
        if self.openai_api_key:
            models.extend(['gpt-3.5-turbo', 'gpt-4'])
        
        if self.anthropic_api_key:
            models.extend(['claude-3-haiku', 'claude-3-sonnet'])
        
        if not models:
            models.append('template-based')
        
        return models

