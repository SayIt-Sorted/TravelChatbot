#!/usr/bin/env python3
"""
Test script for the API handler
Tests the API directly without deploying to Vercel
"""

import json
import sys
import os
from io import BytesIO
from http.server import BaseHTTPRequestHandler

# Add the current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our API handler
from api.index import Handler

def test_api_handler():
    """Test the API handler with a mock request"""
    
    # Create a mock request
    class MockRequest:
        def __init__(self, path, method, body=None):
            self.path = path
            self.method = method
            self.headers = {}
            if body:
                self.headers['Content-Length'] = str(len(body))
            self.body = body or b''
    
    class MockResponse:
        def __init__(self):
            self.status_code = None
            self.headers = {}
            self.body = b''
        
        def write(self, data):
            self.body += data
        
        def getvalue(self):
            return self.body.decode('utf-8')
    
    # Test data
    test_message = "Book a trip from Porto to London next weekend for 3 days under 500 euros. My email is test@example.com"
    test_data = {
        "message": test_message,
        "session_id": "test-session-123"
    }
    
    # Create mock request
    request_body = json.dumps(test_data).encode('utf-8')
    mock_request = MockRequest('/api/chat', 'POST', request_body)
    
    # Create mock response
    mock_response = MockResponse()
    
    # Create handler instance
    handler = Handler()
    handler.rfile = BytesIO(request_body)
    handler.wfile = mock_response
    handler.headers = mock_request.headers
    handler.path = mock_request.path
    
    print("🧪 Testing API Handler")
    print("=" * 50)
    print(f"📝 Test message: {test_message}")
    print()
    
    try:
        # Test the handler
        handler.do_POST()
        
        # Parse response
        response_data = json.loads(mock_response.getvalue())
        
        print("✅ API Response:")
        print(json.dumps(response_data, indent=2))
        
        # Check response structure
        if 'session_id' in response_data and 'response' in response_data:
            response = response_data['response']
            print(f"\n📊 Response Type: {response.get('type', 'unknown')}")
            print(f"💬 Message: {response.get('message', 'No message')}")
            
            if response.get('type') == 'success':
                print("🎉 SUCCESS: API is working correctly!")
            elif response.get('type') == 'question':
                print("❓ QUESTION: API is asking for more info")
            elif response.get('type') == 'error':
                print("❌ ERROR: API encountered an error")
            else:
                print("⚠️ UNKNOWN: Unexpected response type")
        else:
            print("❌ ERROR: Invalid response structure")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api_handler() 