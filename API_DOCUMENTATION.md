# Cognitive Persuasion Engine API Documentation

## Overview
The Cognitive Persuasion Engine API provides AI-powered content generation, audience analysis, and payment processing capabilities.

## Base URL
- **Development**: `http://localhost:5000`
- **Production**: `https://cognitive-persuasion-backend.onrender.com`
- **Custom Domain**: `https://api.visitorintel.site`

## Authentication
All protected endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Demo Mode
- Users with email `demo@example.com` automatically use mock data
- No API keys required for demo functionality
- All features available for testing

## API Endpoints

### Authentication (`/api/auth`)
- `POST /register` - Register new user
- `POST /login` - User login
- `POST /logout` - User logout
- `GET /profile` - Get user profile

### AI Content Generation (`/api/ai`)
- `POST /generate-content` - Generate content with OpenAI
- `POST /research` - Research with Perplexity
- `POST /analyze` - Analyze with Claude
- `POST /strategy` - Generate strategy with Gemini
- `POST /comprehensive` - Run all AI analyses
- `GET /api-status` - Check API availability

### Audience Analysis (`/api/ai`)
- `POST /analyze-audience/twitter` - Twitter audience analysis
- `POST /analyze-audience/linkedin` - LinkedIn professional search
- `POST /analyze-audience/youtube` - YouTube content analysis
- `POST /analyze-audience/reddit` - Reddit community insights
- `POST /audience-research` - Comprehensive multi-platform research

### PayPal Payments (`/api/paypal`)
- `POST /create-payment` - Create PayPal payment
- `POST /execute-payment` - Execute approved payment
- `GET /payment-details/<id>` - Get payment details
- `POST /create-subscription-plan` - Create subscription plan
- `GET /pricing-plans` - Get available pricing plans
- `POST /webhook` - PayPal webhook handler

### Business Management (`/api/businesses`)
- `GET /` - Get user businesses
- `POST /` - Create new business
- `PUT /<id>` - Update business
- `DELETE /<id>` - Delete business

### Audience Management (`/api/audiences`)
- `GET /` - Get user audiences
- `POST /` - Create new audience
- `PUT /<id>` - Update audience
- `DELETE /<id>` - Delete audience

## Request/Response Examples

### Generate Content with OpenAI
```bash
POST /api/ai/generate-content
Content-Type: application/json
Authorization: Bearer <token>

{
  "prompt": "Create a compelling headline for a fitness app",
  "business_type": "fitness",
  "target_audience": "busy professionals"
}
```

Response:
```json
{
  "success": true,
  "data": {
    "success": true,
    "content": {
      "headline": "Transform Your Body in Just 15 Minutes a Day",
      "message": "Discover how busy professionals achieve remarkable fitness results...",
      "cta": "Start Your Transformation Today!",
      "triggers": ["urgency", "social_proof", "transformation"],
      "social_proof": "Over 10,000 professionals trust our solution"
    },
    "source": "openai"
  },
  "message": "Content generated successfully",
  "demo_mode": false
}
```

### Create PayPal Payment
```bash
POST /api/paypal/create-payment
Content-Type: application/json
Authorization: Bearer <token>

{
  "amount": 29.99,
  "currency": "USD",
  "description": "Starter Plan - 1,000 Credits"
}
```

Response:
```json
{
  "success": true,
  "data": {
    "success": true,
    "payment_id": "PAYID-123456789",
    "approval_url": "https://www.paypal.com/checkoutnow?token=EC-123456789",
    "amount": 29.99,
    "currency": "USD",
    "status": "created",
    "source": "paypal"
  },
  "message": "Payment created successfully",
  "demo_mode": false
}
```

## Environment Variables

### Required for Production
```bash
# Flask
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret

# Database
DATABASE_URL=sqlite:///cognitive_persuasion.db

# AI APIs (optional - uses mock data if not provided)
OPENAI_API_KEY=sk-...
PERPLEXITY_API_KEY=pplx-...
CLAUDE_API_KEY=sk-ant-...
GEMINI_API_KEY=AI...

# PayPal (optional - uses mock data if not provided)
PAYPAL_CLIENT_ID=your-client-id
PAYPAL_CLIENT_SECRET=your-client-secret
PAYPAL_MODE=sandbox
```

## Error Handling
All endpoints return consistent error responses:
```json
{
  "error": "Error message description",
  "code": "ERROR_CODE",
  "details": {}
}
```

## Rate Limiting
- Default: 100 requests per minute per IP
- Authenticated users: Higher limits based on subscription
- Demo mode: Standard rate limits apply

## Pricing Plans

### Starter Plan - $29.99/month
- 1,000 AI-generated contents
- OpenAI content generation
- Basic audience analysis
- Email support

### Professional Plan - $79.99/month
- 5,000 AI-generated contents
- All AI APIs (OpenAI, Perplexity, Claude, Gemini)
- Advanced audience insights
- Priority support

### Enterprise Plan - $199.99/month
- Unlimited AI-generated contents
- All features included
- Custom integrations
- Dedicated account manager

## Webhook Configuration
For PayPal webhooks, configure the following URL:
```
https://your-domain.com/api/paypal/webhook
```

Events handled:
- `PAYMENT.SALE.COMPLETED`
- `BILLING.SUBSCRIPTION.CREATED`
- `BILLING.SUBSCRIPTION.CANCELLED`

