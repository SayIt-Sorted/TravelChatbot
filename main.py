"""
Travel Booking AI - Backend API
FastAPI backend for AI-powered travel booking chatbot

API Endpoints:
- POST /api/chat - Process chat messages
- GET /api/health - Health check
- DELETE /api/session/{session_id} - Clear session
- GET /api/config/status - Configuration status
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
from travel_ai import TravelAI
from search_service import SearchService
from email_service import EmailService
from gmail_auth import CustomerGmailLogin
from models import TravelRequest
from config import config
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Pydantic models for API
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: Dict[str, Any]
    session_id: str

class HealthResponse(BaseModel):
    status: str
    message: str

class ConfigStatusResponse(BaseModel):
    openai_configured: bool
    amadeus_configured: bool
    email_configured: bool

# Initialize FastAPI app
app = FastAPI(
    title="Travel Booking AI API",
    description="AI-powered travel booking chatbot API for remote workers",
    version="1.0.0"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173", 
        "https://*.vercel.app",
        "https://*.netlify.app",
        "https://*.github.io",
        "https://your-react-frontend.vercel.app"  # Add your React frontend URL here
    ],  # Configure for your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TravelBookingAPI:
    """API wrapper for Travel Booking AI"""
    
    def __init__(self):
        self.ai = TravelAI()
        self.search = SearchService()
        self.email = EmailService()
        self.customer_login = CustomerGmailLogin()
        self.sessions = {}
    
    def process_message(self, user_id: str, message: str) -> dict:
        """Process user message and return response"""
        
        # Get current session
        current_request = self.sessions.get(user_id)
        
        # Extract information and generate follow-up questions
        ai_result = self.ai.extract_travel_info(message, current_request)
        
        # Auto-fill email if customer is logged in
        if self.customer_login.is_logged_in() and not ai_result["travel_request"].user_email:
            ai_result["travel_request"].user_email = self.customer_login.get_customer_email()
        
        # Update session
        self.sessions[user_id] = ai_result["travel_request"]
        
        # Check if we have all required information
        if ai_result["is_complete"] and ai_result["travel_request"].is_complete():
            return self._handle_complete_request(user_id, ai_result["travel_request"])
        else:
            # Return follow-up question
            follow_up = ai_result.get("follow_up_question")
            if not follow_up:
                follow_up = self.ai.generate_follow_up_question(ai_result["travel_request"])
            
            return {
                "type": "question",
                "message": follow_up,
                "session_id": user_id
            }
    
    def _handle_complete_request(self, user_id: str, request: TravelRequest) -> dict:
        """Handle complete travel request"""
        
        # Search for best travel package
        try:
            package = self.search.search_best_package(request)
        except Exception as e:
            package = None
        
        # Send package via email
        email_sent = self.email.send_travel_package(request, package)
        
        # Clear session
        if user_id in self.sessions:
            del self.sessions[user_id]
        
        # Return response
        if package:
            response = f"""
🎉 Perfect! I found a great travel package for you:

{package.format_summary()}

📧 I've sent the complete details with booking links to {request.user_email}

Ready to plan another trip? Just tell me where you'd like to go next!
            """
        else:
            response = f"""
😔 I couldn't find any travel packages matching your criteria:

📍 Route: {request.origin} → {request.destination}
📅 Date: {request.departure_date.strftime('%B %d, %Y')}
👥 Travelers: {request.passengers}
{f'💰 Budget: €{request.budget}' if request.budget else ''}

📧 I've sent this information to {request.user_email}

Try adjusting your criteria or different dates. Want to search again?
            """
        
        return {
            "type": "complete",
            "message": response.strip(),
            "session_id": user_id,
            "package": package.to_dict() if package else None,
            "email_sent": email_sent
        }

# Initialize the API
api = TravelBookingAPI()

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Handle chat messages"""
    try:
        message = request.message.strip()
        session_id = request.session_id
        
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Process the message
        response = api.process_message(session_id, message)
        
        return ChatResponse(
            response=response,
            session_id=session_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/health", response_model=HealthResponse)
async def health():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        message="Travel Booking API is running"
    )

@app.delete("/api/session/{session_id}")
async def clear_session(session_id: str):
    """Clear a user session"""
    if session_id in api.sessions:
        del api.sessions[session_id]
    return {"message": "Session cleared"}

@app.get("/api/config/status", response_model=ConfigStatusResponse)
async def config_status():
    """Get configuration status"""
    return ConfigStatusResponse(
        openai_configured=bool(config.get_openai_api_key()),
        amadeus_configured=bool(config.get_amadeus_api_key()),
        email_configured=bool(config.get_smtp_email())
    )

@app.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "message": "Travel Booking AI API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }

if __name__ == "__main__":
    import uvicorn
    
    # Check configuration
    if not config.get_openai_api_key():
        print("❌ OpenAI API key is required!")
        print("Set OPENAI_API_KEY in your .env file")
        exit(1)
    
    print("🚀 Starting Travel Booking API...")
    print("📡 API: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 