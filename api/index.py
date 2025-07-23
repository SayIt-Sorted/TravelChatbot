"""
Minimal Vercel entry point
"""
from http.server import BaseHTTPRequestHandler
import json

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
                "error": "Endpoint not found",
                "available": ["/", "/api/health", "/api/chat"]
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
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            
            try:
                data = json.loads(body)
                message = data.get('message', '')
                
                # Simple response for now
                response = {
                    "response": {
                        "type": "question",
                        "message": f"I received your message: '{message}'. The full AI backend is being set up.",
                        "session_id": "test-session"
                    },
                    "session_id": "test-session"
                }
            except:
                response = {
                    "error": "Invalid JSON in request body"
                }
        else:
            response = {
                "error": "Endpoint not found"
            }
        
        self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

# Export for Vercel
handler = Handler 