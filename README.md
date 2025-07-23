# Travel Booking AI - Backend API

A FastAPI backend for an AI-powered travel booking chatbot designed for remote workers. This API processes natural language travel requests, extracts key information using GPT, searches for flights and accommodations, and sends booking packages via email.

## Features

- 🤖 **AI-Powered**: Uses GPT to extract travel information from natural language
- 🔍 **Smart Search**: Searches for flights and accommodations with budget validation
- 📧 **Email Integration**: Sends complete travel packages via email
- 🔐 **Gmail OAuth**: Optional customer login for email auto-fill
- 🚀 **FastAPI**: Modern, fast REST API with automatic documentation
- 🧪 **Session Management**: Maintains conversation context per user

## API Endpoints

### Core Endpoints

- `POST /api/chat` - Process chat messages and get AI responses
- `GET /api/health` - Health check endpoint
- `DELETE /api/session/{session_id}` - Clear user session
- `GET /api/config/status` - Check service configuration status

### Documentation

- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation

## Quick Start

### 1. Setup Environment

```bash
# Clone the repository
git clone <repository-url>
cd TravelChatbot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file in the root directory:

```env
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional - Email sending
SMTP_EMAIL=your_email@example.com
SMTP_PASSWORD=your_email_password_here

# Optional - Flight search (uses mock data without it)
AMADEUS_API_KEY=your_amadeus_api_key_here
AMADEUS_API_SECRET=your_amadeus_api_secret_here
```

### 3. Run the API

```bash
python main.py
```

The API will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs

## API Usage

### Chat Endpoint

```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Book a trip from Porto to London next weekend for 3 days under 500 euros",
    "session_id": "optional-session-id"
  }'
```

**Response:**
```json
{
  "response": {
    "type": "question",
    "message": "What's your email address?",
    "session_id": "session-uuid"
  },
  "session_id": "session-uuid"
}
```

### Complete Travel Request Response

```json
{
  "response": {
    "type": "complete",
    "message": "🎉 Perfect! I found a great travel package...",
    "session_id": "session-uuid",
    "package": {
      "flight": {...},
      "accommodation": {...}
    },
    "email_sent": true
  },
  "session_id": "session-uuid"
}
```

## Frontend Integration

### React Example

```javascript
const sendMessage = async (message, sessionId = null) => {
  try {
    const response = await fetch('http://localhost:8000/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: message,
        session_id: sessionId
      })
    });
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error:', error);
  }
};

// Usage
const result = await sendMessage("Book a trip to Paris next month");
console.log(result.response.message);
```

### JavaScript/TypeScript Example

```typescript
interface ChatRequest {
  message: string;
  session_id?: string;
}

interface ChatResponse {
  response: {
    type: 'question' | 'complete';
    message: string;
    session_id: string;
    package?: any;
    email_sent?: boolean;
  };
  session_id: string;
}

class TravelAPI {
  private baseUrl: string;
  
  constructor(baseUrl: string = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }
  
  async sendMessage(message: string, sessionId?: string): Promise<ChatResponse> {
    const response = await fetch(`${this.baseUrl}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message, session_id: sessionId })
    });
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    return response.json();
  }
  
  async clearSession(sessionId: string): Promise<void> {
    await fetch(`${this.baseUrl}/api/session/${sessionId}`, {
      method: 'DELETE'
    });
  }
  
  async getHealth(): Promise<any> {
    const response = await fetch(`${this.baseUrl}/api/health`);
    return response.json();
  }
}
```

## Architecture

```
TravelChatbot/
├── main.py              # FastAPI application entry point
├── models.py            # Data models and structures
├── travel_ai.py         # AI processing with GPT
├── search_service.py    # Flight and accommodation search
├── email_service.py     # Email sending functionality
├── gmail_auth.py        # Gmail OAuth for customer login
├── config.py            # Configuration management
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Development

### Running Tests

```bash
pytest test_backend.py
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key for GPT integration |
| `SMTP_EMAIL` | No | Email for sending travel packages |
| `SMTP_PASSWORD` | No | Email password |
| `AMADEUS_API_KEY` | No | Amadeus API key for flight search |
| `AMADEUS_API_SECRET` | No | Amadeus API secret |

### Optional Gmail OAuth Setup

For customer email auto-fill functionality:

1. Set up Google OAuth credentials
2. Configure in `gmail_auth.py`
3. Customers can login with Gmail to auto-fill their email

## Production Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Configuration

For production, configure:
- CORS origins for your frontend domain
- Secure SMTP settings
- Environment-specific API keys
- Session storage (Redis recommended for scale)

## License

[Your License Here] 