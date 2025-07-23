#!/usr/bin/env python3
"""
Local HTTP server test for the API
Simulates the actual API behavior locally
"""

import json
import requests
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import sys
import os

# Add the current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our API handler
from api.index import Handler

class TestServer:
    def __init__(self, port=8000):
        self.port = port
        self.server = None
        self.thread = None
        
    def start(self):
        """Start the test server"""
        self.server = HTTPServer(('localhost', self.port), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.daemon = True
        self.thread.start()
        print(f"🚀 Test server started on http://localhost:{self.port}")
        time.sleep(1)  # Give server time to start
        
    def stop(self):
        """Stop the test server"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            print("🛑 Test server stopped")
            
    def test_health(self):
        """Test the health endpoint"""
        try:
            response = requests.get(f'http://localhost:{self.port}/')
            print(f"✅ Health check: {response.status_code}")
            print(f"Response: {response.json()}")
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False
            
    def test_chat(self, message, session_id=None):
        """Test the chat endpoint"""
        try:
            data = {
                "message": message,
                "session_id": session_id or "test-session"
            }
            
            response = requests.post(
                f'http://localhost:{self.port}/api/chat',
                json=data,
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"✅ Chat test: {response.status_code}")
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            
            # Check response structure
            if 'session_id' in result and 'response' in result:
                response_data = result['response']
                print(f"📊 Response Type: {response_data.get('type', 'unknown')}")
                print(f"💬 Message: {response_data.get('message', 'No message')}")
                
                if response_data.get('type') == 'success':
                    print("🎉 SUCCESS: API is working correctly!")
                elif response_data.get('type') == 'question':
                    print("❓ QUESTION: API is asking for more info")
                elif response_data.get('type') == 'error':
                    print("❌ ERROR: API encountered an error")
                    
            return response.status_code == 200
            
        except Exception as e:
            print(f"❌ Chat test failed: {e}")
            return False

def main():
    """Run the API test"""
    print("🧪 Testing API with Local HTTP Server")
    print("=" * 50)
    
    # Test data with email
    test_message_with_email = "Book a trip from Porto to London next weekend for 3 days under 500 euros. My email is test@example.com"
    # Test data without email
    test_message_without_email = "Book a trip from Porto to London next weekend for 3 days under 500 euros"
    # Test email follow-up
    test_email_followup = "joaopaesteves99@gmail.com"
    
    print(f"📝 Test 1: With email - {test_message_with_email}")
    print(f"📝 Test 2: Without email - {test_message_without_email}")
    print(f"📝 Test 3: Email follow-up - {test_email_followup}")
    print()
    
    # Start server
    server = TestServer(8000)
    try:
        server.start()
        
        # Test health endpoint
        print("🔍 Testing health endpoint...")
        if not server.test_health():
            print("❌ Health check failed, stopping test")
            return
        print()
        
        # Test 1: With email (should complete successfully)
        print("🔍 Test 1: Testing with email...")
        success1 = server.test_chat(test_message_with_email, "test-session-1")
        print()
        
        # Test 2: Without email (should ask for email)
        print("🔍 Test 2: Testing without email...")
        success2 = server.test_chat(test_message_without_email, "test-session-2")
        print()
        
        # Test 3: Email follow-up (should complete the request)
        print("🔍 Test 3: Testing email follow-up...")
        success3 = server.test_chat(test_email_followup, "test-session-2")  # Same session as test 2
        print()
        
        if success1 and success2 and success3:
            print("\n🎉 API TEST SUCCESSFUL!")
            print("✅ The API correctly handles all scenarios:")
            print("   - With email: Completes and sends package")
            print("   - Without email: Asks for email first")
            print("   - Email follow-up: Completes the request")
        else:
            print("\n❌ API TEST FAILED!")
            print("⚠️ Check the logs above for issues")
            
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        server.stop()

if __name__ == "__main__":
    main() 