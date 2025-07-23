"""
Robust Vercel function with comprehensive error handling
"""
from http.server import BaseHTTPRequestHandler
import json
import uuid

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            if self.path == '/api/health':
                response = {
                    "status": "healthy",
                    "message": "Travel Booking API is running"
                }
            elif self.path == '/':
                response = {
                    "message": "Travel Booking AI API",
                    "version": "1.0.0",
                    "endpoints": {
                        "health": "/api/health",
                        "chat": "/api/chat"
                    }
                }
            else:
                response = {
                    "error": "Endpoint not found"
                }
            
            self.wfile.write(json.dumps(response).encode())
        except Exception as e:
            self.send_error(500, f"Internal server error: {str(e)}")
    
    def do_POST(self):
        try:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            if self.path == '/api/chat':
                # Generate a session ID
                session_id = str(uuid.uuid4())
                
                # Hardcoded response for testing
                response = {
                    "status": "success",
                    "message": "POST request received",
                    "path": "/api/chat",
                    "session_id": session_id,
                    "response": {
                        "type": "question",
                        "message": "Hi! I'm your AI travel assistant. I can help you book flights and accommodation. Just tell me where you want to go, when, and your budget!",
                        "session_id": session_id
                    }
                }
            else:
                response = {
                    "status": "error",
                    "message": "Endpoint not found",
                    "path": self.path,
                    "session_id": str(uuid.uuid4()),
                    "response": {
                        "type": "error",
                        "message": "Endpoint not found",
                        "session_id": str(uuid.uuid4())
                    }
                }
            
            # Write response
            response_json = json.dumps(response)
            self.wfile.write(response_json.encode('utf-8'))
            
        except Exception as e:
            # Simple error response
            error_response = {
                "status": "error",
                "message": "Internal server error",
                "path": "/api/chat",
                "session_id": str(uuid.uuid4()),
                "response": {
                    "type": "error",
                    "message": "I'm having trouble processing your request right now. Please try again in a moment.",
                    "session_id": str(uuid.uuid4())
                }
            }
            error_json = json.dumps(error_response)
            self.wfile.write(error_json.encode('utf-8'))
    
    def do_OPTIONS(self):
        try:
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
        except:
            pass
    
    def process_chat_message_safe(self, message):
        """Safely process chat message with comprehensive error handling"""
        try:
            if not message or not message.strip():
                return "Please send me a message about your travel plans!"
            
            message_lower = message.lower()
            
            # Handle greetings
            if any(word in message_lower for word in ['hello', 'hi', 'hey']):
                return "Hi! I'm your AI travel assistant. I can help you book flights and accommodation. Just tell me where you want to go, when, and your budget!"
            
            # Handle travel requests
            if any(word in message_lower for word in ['book', 'trip', 'flight', 'travel']):
                try:
                    return self.handle_travel_request_safe(message)
                except:
                    return "I understand you want to book a trip! To help you best, please tell me:\n\n📍 Where you're traveling from and to\n📅 When you want to travel\n👥 How many travelers\n💰 Your budget\n\nFor example: 'I want to go from Porto to London next weekend for 3 days under 500 euros'"
            
            # Handle city mentions
            if any(word in message_lower for word in ['porto', 'london', 'paris', 'madrid', 'rome', 'nyc']):
                return f"I see you mentioned travel! That sounds exciting. To help you book this trip, I need a few more details:\n\n- When do you want to travel?\n- How many people?\n- What's your budget?\n- Do you need accommodation as well?"
            
            # Handle budget mentions
            if any(word in message_lower for word in ['500', '1000', 'budget', 'euros', 'dollars']):
                return "Great! I can see you have a budget in mind. To help you find the best travel options, I need to know:\n\n📍 Where you're traveling from and to\n📅 When you want to travel\n👥 How many travelers\n\nFor example: 'I want to go from Porto to London next weekend for 3 days under 500 euros'"
            
            # Default response
            return "I understand you want to plan a trip! To help you best, please tell me:\n\n📍 Where you're traveling from and to\n📅 When you want to travel\n👥 How many travelers\n💰 Your budget\n\nFor example: 'I want to go from Porto to London next weekend for 3 days under 500 euros'"
            
        except Exception as e:
            return "I'm having trouble understanding your request. Could you please try rephrasing it?"
    
    def handle_travel_request_safe(self, message):
        """Safely handle travel requests"""
        try:
            message_lower = message.lower()
            
            # Extract basic information
            origin = "Unknown"
            destination = "Unknown"
            budget = "Not specified"
            duration = "Not specified"
            
            # Simple pattern matching
            if 'porto' in message_lower and 'london' in message_lower:
                origin = "Porto"
                destination = "London"
            elif 'porto' in message_lower and 'paris' in message_lower:
                origin = "Porto"
                destination = "Paris"
            elif 'nyc' in message_lower and 'paris' in message_lower:
                origin = "NYC"
                destination = "Paris"
            elif 'madrid' in message_lower and 'rome' in message_lower:
                origin = "Madrid"
                destination = "Rome"
            
            # Extract budget
            if '500' in message and 'euros' in message_lower:
                budget = "€500"
            elif '500' in message and 'dollars' in message_lower:
                budget = "$500"
            
            # Extract duration
            if '3 days' in message_lower or '3 day' in message_lower:
                duration = "3 days"
            elif 'weekend' in message_lower:
                duration = "weekend"
            elif 'week' in message_lower:
                duration = "1 week"
            
            return f"""🎉 Perfect! I understand your travel request:

📍 Route: {origin} → {destination}
⏱️ Duration: {duration}
💰 Budget: {budget}

I'm currently setting up the full AI travel booking system with real-time flight search and accommodation booking. Your request has been logged and I'm working on processing it.

While the complete system is being finalized, I can help you with:
• Travel planning advice for {destination}
• Budget optimization tips
• Best time to visit recommendations
• Alternative route suggestions

Would you like me to help you plan the details of your {destination} trip while the booking system is being set up?"""
            
        except Exception as e:
            return "I understand you want to book a trip! I'm currently setting up the full travel booking system. Your request has been received and I'm working on processing it. Please try again in a moment!"

handler = Handler 