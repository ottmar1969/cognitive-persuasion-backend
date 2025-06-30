# Cognitive Persuasion Engine - Backend API

A Flask-based backend API for the Cognitive Persuasion Engine, featuring multi-AI integration, user management, and payment processing.

## Features

- 🤖 **Multi-AI Integration**: OpenAI, Google Gemini, Claude, and Perplexity
- 👥 **User Management**: JWT-based authentication and authorization
- 💳 **Payment System**: PayPal integration with credit-based pricing
- 🏢 **Business Management**: Support for multiple business types and audiences
- 🎯 **Target Audience**: Manual and predefined audience management
- 🔒 **Security**: CORS, rate limiting, and secure password hashing

## Quick Deploy

### Deploy to Render (Recommended)
1. Fork this repository
2. Go to [Render](https://render.com) and create a new Web Service
3. Connect your GitHub repository
4. Set environment variables (see `.env.example`)
5. Deploy!

### Deploy to Railway
1. Fork this repository
2. Go to [Railway](https://railway.app) and create a new project
3. Connect your GitHub repository
4. Set environment variables
5. Deploy!

### Deploy with Docker
```bash
docker build -t cognitive-persuasion-api .
docker run -p 5000:5000 --env-file .env cognitive-persuasion-api
```

## Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

### Required Variables:
- `SECRET_KEY`: Flask secret key
- `OPENAI_API_KEY`: OpenAI API key for GPT models
- `GOOGLE_API_KEY`: Google API key for Gemini
- `CLAUDE_API_KEY`: Anthropic API key for Claude
- `PERPLEXITY_API_KEY`: Perplexity API key
- `PAYPAL_CLIENT_ID`: PayPal client ID
- `PAYPAL_CLIENT_SECRET`: PayPal client secret

## Local Development

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ottmar1969/cognitive-persuasion-backend.git
   cd cognitive-persuasion-backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Run the application**:
   ```bash
   python src/main.py
   ```

The API will be available at `http://localhost:5000`

## API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/profile` - Get user profile

### Business Management
- `GET /api/businesses` - List user businesses
- `POST /api/businesses` - Create new business
- `PUT /api/businesses/{id}` - Update business
- `DELETE /api/businesses/{id}` - Delete business

### AI Sessions
- `POST /api/ai-sessions` - Create AI conversation session
- `GET /api/ai-sessions/{id}` - Get session details
- `POST /api/ai-sessions/{id}/regenerate` - Regenerate responses

### Payment
- `GET /api/payment/packages` - Get credit packages
- `POST /api/payment/purchase` - Purchase credits
- `GET /api/payment/balance` - Get credit balance

## Deployment Configuration Files

- `Procfile` - Heroku/Render deployment
- `nixpacks.toml` - Railway deployment
- `Dockerfile` - Container deployment
- `runtime.txt` - Python version specification
- `requirements.txt` - Python dependencies

## Architecture

```
src/
├── main.py              # Application entry point
├── models/              # Database models
│   ├── user_simple.py   # User model
│   └── free_trial.py    # Free trial model
├── routes/              # API routes
│   ├── auth_simple.py   # Authentication routes
│   ├── business_simple.py # Business management
│   ├── audience_simple.py # Audience management
│   ├── payment_simple.py  # Payment processing
│   └── ai_session_enhanced.py # AI session handling
└── utils/               # Utility functions
    ├── multi_ai_service_enhanced.py # AI service integration
    └── init_data_simple.py # Database initialization
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support, please contact [your-email@example.com] or create an issue on GitHub.

