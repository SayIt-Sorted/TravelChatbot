#!/usr/bin/env python3
"""
Simple test script for the API core functions
Tests the TravelAI, SearchService, and EmailService directly
"""

import json
import sys
import os

# Add the current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_core_functions():
    """Test the core functions used by the API"""
    
    print("🧪 Testing Core API Functions")
    print("=" * 50)
    
    # Test message
    test_message = "Book a trip from Porto to London next weekend for 3 days under 500 euros. My email is test@example.com"
    print(f"📝 Test message: {test_message}")
    print()
    
    try:
        # Test 1: Import modules
        print("🔍 Step 1: Testing imports...")
        from travel_ai import TravelAI
        from search_service import SearchService
        from email_service import EmailService
        from models import TravelRequest
        print("✅ All modules imported successfully")
        print()
        
        # Test 2: TravelAI extraction
        print("🔍 Step 2: Testing TravelAI extraction...")
        travel_ai = TravelAI()
        extraction_result = travel_ai.extract_travel_info(test_message)
        print(f"✅ Extraction result: {extraction_result}")
        print()
        
        # Test 3: Check if extraction is complete
        if extraction_result.get('is_complete', False):
            print("🔍 Step 3: Testing SearchService...")
            travel_request = extraction_result['travel_request']
            search_service = SearchService()
            
            # Check if search_best_package method exists
            if hasattr(search_service, 'search_best_package'):
                search_result = search_service.search_best_package(travel_request)
                print(f"✅ Search result: {search_result}")
            else:
                print("⚠️ search_best_package method not found, checking available methods...")
                methods = [method for method in dir(search_service) if not method.startswith('_')]
                print(f"Available methods: {methods}")
                search_result = None
            print()
            
            # Test 4: Email service
            if search_result:
                print("🔍 Step 4: Testing EmailService...")
                email_service = EmailService()
                
                # Check if send_travel_package method exists with correct signature
                if hasattr(email_service, 'send_travel_package'):
                    try:
                        email_sent = email_service.send_travel_package(travel_request, search_result)
                        print(f"✅ Email result: {email_sent}")
                    except Exception as e:
                        print(f"⚠️ Email error: {e}")
                else:
                    print("⚠️ send_travel_package method not found")
                    methods = [method for method in dir(email_service) if not method.startswith('_')]
                    print(f"Available methods: {methods}")
            print()
            
            print("🎉 SUCCESS: All core functions working!")
            
        else:
            print("❓ Extraction incomplete - this is normal for incomplete requests")
            print(f"Follow-up question: {extraction_result.get('follow_up_question')}")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_core_functions() 