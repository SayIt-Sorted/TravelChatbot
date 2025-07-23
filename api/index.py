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
        
        self.wfile.write(json.dumps(response).encode())
    
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
        
        self.wfile.write(json.dumps(response).encode())
    
    def process_travel_request(self, message: str, session_id: str) -> dict:
        """Process travel request with AI, search, and email"""
        try:
            # Initialize services
            travel_ai = TravelAI()
            search_service = SearchService()
            email_service = EmailService()
            
            # Step 1: Extract travel information
            extraction_result = travel_ai.extract_travel_info(message)
            
            if not extraction_result.get('is_complete', False):
                # Ask follow-up question
                follow_up = extraction_result.get('follow_up_question', 'Could you provide more details about your trip?')
                return {
                    "session_id": session_id,
                    "response": {
                        "type": "question",
                        "message": follow_up,
                        "session_id": session_id,
                        "extraction": extraction_result
                    }
                }
            
            # Step 2: Create travel request
            extracted_info = extraction_result['extracted_info']
            travel_request = TravelRequest(
                origin=extracted_info.get('origin'),
                destination=extracted_info.get('destination'),
                departure_date=datetime.strptime(extracted_info['departure_date'], '%Y-%m-%d').date() if extracted_info.get('departure_date') else None,
                return_date=datetime.strptime(extracted_info['return_date'], '%Y-%m-%d').date() if extracted_info.get('return_date') else None,
                duration_days=extracted_info.get('duration_days'),
                passengers=extracted_info.get('passengers', 1),
                budget=extracted_info.get('budget'),
                user_email=extracted_info.get('user_email')
            )
            
            # Step 3: Search for travel package
            search_result = search_service.search_travel_package(travel_request)
            
            if not search_result.get('found', False):
                return {
                    "session_id": session_id,
                    "response": {
                        "type": "no_results",
                        "message": "I couldn't find any travel packages matching your criteria. Try adjusting your budget or dates.",
                        "session_id": session_id,
                        "travel_request": extracted_info
                    }
                }
            
            # Step 4: Send email
            package = search_result['package']
            email_sent = email_service.send_travel_package(
                to_email=travel_request.user_email,
                travel_request=travel_request,
                package=package
            )
            
            # Step 5: Return success response
            return {
                "session_id": session_id,
                "response": {
                    "type": "success",
                    "message": f"Perfect! I found a great travel package for {travel_request.origin} to {travel_request.destination}. I've sent the details to {travel_request.user_email}.",
                    "session_id": session_id,
                    "travel_request": extracted_info,
                    "package": package,
                    "email_sent": email_sent
                }
            }
            
        except Exception as e:
            return {
                "session_id": session_id,
                "response": {
                    "type": "error",
                    "message": f"Sorry, I encountered an error while processing your request: {str(e)}",
                    "session_id": session_id
                }
            }
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

handler = Handler 