"""
Super Simple Vercel API for testing
"""
from http.server import BaseHTTPRequestHandler
import json
import uuid

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "status": "healthy",
            "message": "Simple Travel API is running",
            "endpoints": ["/api/chat"]
        }
        
        self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        if self.path == '/api/chat':
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))
            
            message = data.get('message', '')
            session_id = data.get('session_id') or str(uuid.uuid4())
            
            # Simple response for now
            response = {
                "session_id": session_id,
                "response": {
                    "type": "question",
                    "message": f"I received: '{message}'. This is the simple API version.",
                    "session_id": session_id
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

handler = Handler 