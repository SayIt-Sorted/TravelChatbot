"""
Full Travel AI API for Vercel
Handles chat messages with AI processing, search, and email sending
"""
from http.server import BaseHTTPRequestHandler
import json
import uuid
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from travel_ai import TravelAI
    from search_service import SearchService
    from email_service import EmailService
    from models import TravelRequest
    from config import config
    MODULES_LOADED = True
except ImportError as e:
    print(f"Import error: {e}")
    MODULES_LOADED = False

# Global session storage (in production, use Redis or database)
SESSIONS = {}

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "status": "healthy",
            "message": "Travel AI API is running",
            "modules_loaded": MODULES_LOADED,
            "endpoints": ["/api/chat"]
        }
        
        self.wfile.write(json.dumps(response, default=str).encode())
    
    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        if self.path == '/api/chat':
            try:
                # Read request body
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length)
                data = json.loads(body.decode('utf-8'))
                
                message = data.get('message', '')
                session_id = data.get('session_id') or str(uuid.uuid4())
                
                if not MODULES_LOADED:
                    response = {
                        "session_id": session_id,
                        "response": {
                            "type": "error",
                            "message": "API modules not loaded properly",
                            "session_id": session_id
                        }
                    }
                else:
                    # Process with full TravelAI
                    response = self.process_travel_request(message, session_id)
                    
            except Exception as e:
                response = {
                    "session_id": str(uuid.uuid4()),
                    "response": {
                        "type": "error",
                        "message": f"Error processing request: {str(e)}",
                        "session_id": str(uuid.uuid4())
                    }
                }
        else:
            response = {
                "session_id": str(uuid.uuid4()),
                "response": {
                    "type": "error",
                    "message": "Endpoint not found",
                    "session_id": str(uuid.uuid4())
                }
            }
        
        self.wfile.write(json.dumps(response, default=str).encode())
    
    def process_travel_request(self, message: str, session_id: str) -> dict:
        """Process travel request with AI, search, and email"""
        try:
            # Initialize services
            travel_ai = TravelAI()
            search_service = SearchService()
            email_service = EmailService()
            
            # Get existing session data
            session_data = SESSIONS.get(session_id, {})
            current_request = session_data.get('travel_request')
            
            # Check if this looks like just an email address
            if self._is_email_only(message) and current_request and not current_request.user_email:
                # User is providing email for existing request
                email = message.strip()
                current_request.user_email = email
                SESSIONS[session_id] = {'travel_request': current_request}
                
                # Now search and send email
                return self._complete_travel_request(current_request, session_id, search_service, email_service)
            
            # Step 1: Extract travel information (with current request context)
            extraction_result = travel_ai.extract_travel_info(message, current_request)
            
            # Debug: Print what we got from TravelAI
            print(f"Extraction result: {extraction_result}")
            
            # Check if extraction failed
            if not extraction_result or 'travel_request' not in extraction_result:
                return {
                    "session_id": session_id,
                    "response": {
                        "type": "question",
                        "message": "I'm sorry, I didn't understand that. Could you please tell me where you'd like to travel from and to?",
                        "session_id": session_id
                    }
                }
            
            # Update session with new travel request
            travel_request = extraction_result['travel_request']
            SESSIONS[session_id] = {'travel_request': travel_request}
            
            if not extraction_result.get('is_complete', False):
                # Ask follow-up question
                follow_up = extraction_result.get('follow_up_question', 'Could you provide more details about your trip?')
                return {
                    "session_id": session_id,
                    "response": {
                        "type": "question",
                        "message": follow_up,
                        "session_id": session_id,
                        "extraction": extraction_result.get('extracted_info', {})
                    }
                }
            
            # Check if email is missing (most important)
            if not travel_request.user_email:
                return {
                    "session_id": session_id,
                    "response": {
                        "type": "question",
                        "message": "Great! I have all the details I need. What's your email address so I can send you the travel package?",
                        "session_id": session_id,
                        "extraction": extraction_result.get('extracted_info', {})
                    }
                }
            
            # Complete the travel request
            return self._complete_travel_request(travel_request, session_id, search_service, email_service)
            
        except Exception as e:
            print(f"Error in process_travel_request: {e}")
            import traceback
            traceback.print_exc()
            return {
                "session_id": session_id,
                "response": {
                    "type": "error",
                    "message": f"Sorry, I encountered an error while processing your request: {str(e)}"
                }
            }
    
    def _is_email_only(self, message: str) -> bool:
        """Check if message is just an email address"""
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, message.strip()))
    
    def _complete_travel_request(self, travel_request: TravelRequest, session_id: str, search_service, email_service) -> dict:
        """Complete travel request with search and email"""
        # Search for travel package
        search_result = search_service.search_best_package(travel_request)
        
        if not search_result:
            return {
                "session_id": session_id,
                "response": {
                    "type": "no_results",
                    "message": "I couldn't find any travel packages matching your criteria. Try adjusting your budget or dates.",
                    "travel_request": travel_request.model_dump()
                }
            }
        
        # Send email
        email_sent = email_service.send_travel_package(travel_request, search_result)
        
        # Clear session after completion
        if session_id in SESSIONS:
            del SESSIONS[session_id]
        
        # Return success response
        return {
            "session_id": session_id,
            "response": {
                "type": "success",
                "message": f"Perfect! I found a great travel package for {travel_request.origin} to {travel_request.destination}. I've sent the details to {travel_request.user_email}. Check your email for the complete booking information!",
                "travel_request": travel_request.model_dump(),
                "package": search_result.to_dict() if hasattr(search_result, 'to_dict') else search_result,
                "email_sent": email_sent,
                "conversation_complete": True
            }
        }
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

handler = Handler 