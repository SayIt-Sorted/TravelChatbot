"""
Vercel function with proper chat response format and better error handling
"""
from http.server import BaseHTTPRequestHandler
import json
import uuid
import traceback

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
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
    
    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        if self.path == '/api/chat':
            try:
                # Read request body
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length)
                
                data = json.loads(body)
                message = data.get('message', '')
                session_id = data.get('session_id') or str(uuid.uuid4())
                
                # Process the message
                ai_response = self.process_chat_message(message)
                
                # Return in the correct format
                response = {
                    "session_id": session_id,
                    "response": {
                        "type": "question",
                        "message": ai_response,
                        "session_id": session_id
                    }
                }
                
            except Exception as e:
                # Log the error for debugging
                error_traceback = traceback.format_exc()
                print(f"Error processing chat: {str(e)}")
                print(f"Traceback: {error_traceback}")
                
                response = {
                    "session_id": str(uuid.uuid4()),
                    "response": {
                        "type": "error",
                        "message": f"Sorry, I encountered an error: {str(e)}. Please try again.",
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
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def process_chat_message(self, message):
        """Process chat message and return AI response"""
        if not message.strip():
            return "Please send me a message about your travel plans!"
        
        # Simple AI processing with better travel request handling
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['hello', 'hi', 'hey']):
            return "Hi! I'm your AI travel assistant. I can help you book flights and accommodation. Just tell me where you want to go, when, and your budget!"
        
        elif any(word in message_lower for word in ['book', 'trip', 'flight', 'travel']):
            # Check if it's a detailed travel request
            if any(word in message_lower for word in ['porto', 'london', 'paris', 'madrid', 'rome', 'nyc', 'euros', 'dollars', 'budget']):
                return self.process_travel_request(message)
            else:
                return "Great! I can help you book a trip. To get started, I need some information:\n\n1. Where are you traveling from?\n2. Where do you want to go?\n3. When do you want to travel?\n4. How many travelers?\n5. What's your budget?\n\nJust tell me these details and I'll find the best options for you!"
        
        elif any(word in message_lower for word in ['porto', 'london', 'paris', 'madrid', 'rome', 'nyc']):
            return f"I see you mentioned travel to {message}. That sounds exciting! To help you book this trip, I need a few more details:\n\n- When do you want to travel?\n- How many people?\n- What's your budget?\n- Do you need accommodation as well?"
        
        else:
            return "I understand you want to plan a trip! To help you best, please tell me:\n\n📍 Where you're traveling from and to\n📅 When you want to travel\n👥 How many travelers\n💰 Your budget\n\nFor example: 'I want to go from Porto to London next weekend for 3 days under 500 euros'"
    
    def process_travel_request(self, message):
        """Process detailed travel requests"""
        try:
            # Extract travel information (simplified parsing)
            message_lower = message.lower()
            
            # Look for common patterns
            if 'porto' in message_lower and 'london' in message_lower:
                origin = "Porto"
                destination = "London"
            elif 'porto' in message_lower and 'paris' in message_lower:
                origin = "Porto"
                destination = "Paris"
            else:
                origin = "Unknown"
                destination = "Unknown"
            
            # Look for budget
            if '500' in message and 'euros' in message_lower:
                budget = "€500"
            elif '500' in message and 'dollars' in message_lower:
                budget = "$500"
            else:
                budget = "Not specified"
            
            # Look for duration
            if '3 days' in message_lower or '3 day' in message_lower:
                duration = "3 days"
            elif 'weekend' in message_lower:
                duration = "weekend"
            else:
                duration = "Not specified"
            
            return f"""🎉 Perfect! I found your travel request:

📍 Route: {origin} → {destination}
⏱️ Duration: {duration}
💰 Budget: {budget}

I'm currently setting up the full AI travel booking system. For now, I can confirm I understand your request:

- You want to travel from {origin} to {destination}
- Duration: {duration}
- Budget: {budget}

The complete booking system with flight search and accommodation will be available soon!

Would you like me to help you with anything else about this trip?"""
            
        except Exception as e:
            return f"I understand you want to book a trip! I'm currently setting up the full travel booking system. Your request has been received and I'm working on processing it. Please try again in a moment, or let me know if you need help with anything else!"

handler = Handler 