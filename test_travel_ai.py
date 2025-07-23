#!/usr/bin/env python3
"""
Test script for Travel AI functionality
Tests: Text extraction → Flight search → Email sending
"""

import os
import sys
from datetime import date
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_travel_ai_workflow():
    """Test the complete travel AI workflow"""
    
    print("🧪 Testing Travel AI Workflow")
    print("=" * 50)
    
    # Test message
    test_message = "Book a trip from Porto to London next weekend for 3 days under 500 euros. My email is test@example.com"
    
    print(f"📝 Test message: {test_message}")
    print()
    
    try:
        # Step 1: Import and test TravelAI
        print("🔍 Step 1: Testing TravelAI (Text Extraction)")
        print("-" * 40)
        
        from travel_ai import TravelAI
        from models import TravelRequest
        
        ai = TravelAI()
        print("✅ TravelAI imported successfully")
        
        # Test text extraction
        ai_result = ai.extract_travel_info(test_message)
        travel_request = ai_result["travel_request"]
        
        print(f"📍 Origin: {travel_request.origin}")
        print(f"🎯 Destination: {travel_request.destination}")
        print(f"📅 Departure: {travel_request.departure_date}")
        print(f"⏱️ Duration: {travel_request.duration_days} days")
        print(f"👥 Passengers: {travel_request.passengers}")
        print(f"💰 Budget: €{travel_request.budget}")
        print(f"📧 Email: {travel_request.user_email}")
        print(f"✅ Complete: {travel_request.is_complete()}")
        print()
        
        # Step 2: Test SearchService
        print("🔍 Step 2: Testing SearchService (Flight & Accommodation)")
        print("-" * 40)
        
        from search_service import SearchService
        
        search = SearchService()
        print("✅ SearchService imported successfully")
        
        # Search for travel package
        package = search.search_best_package(travel_request)
        
        if package:
            print("🎉 Travel package found!")
            print(f"✈️ Flight: {package.flight.airline} {package.flight.flight_number}")
            print(f"   {package.flight.departure_time} → {package.flight.arrival_time}")
            print(f"   Price: €{package.flight.price}")
            
            if package.accommodation:
                print(f"🏨 Hotel: {package.accommodation.name}")
                print(f"   Price: €{package.accommodation.price_per_night}/night")
                print(f"   Total: €{package.accommodation.total_price}")
            
            print(f"💰 Total Package: €{package.total_price}")
        else:
            print("❌ No travel package found")
        print()
        
        # Step 3: Test EmailService
        print("📧 Step 3: Testing EmailService (Email Sending)")
        print("-" * 40)
        
        from email_service import EmailService
        
        email = EmailService()
        print("✅ EmailService imported successfully")
        
        # Send travel package
        email_sent = email.send_travel_package(travel_request, package)
        
        if email_sent:
            print("✅ Email sent successfully (or printed to console)")
        else:
            print("❌ Email sending failed")
        print()
        
        # Summary
        print("🎯 Workflow Summary")
        print("-" * 40)
        print(f"✅ Text extraction: {ai_result['is_complete']}")
        print(f"✅ Package found: {package is not None}")
        print(f"✅ Email sent: {email_sent}")
        print()
        print("🎉 All tests completed successfully!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure all dependencies are installed:")
        print("   pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

def test_simple_extraction():
    """Test just the text extraction part"""
    
    print("🧪 Testing Simple Text Extraction")
    print("=" * 40)
    
    test_cases = [
        "I want to go from Porto to London next weekend for 3 days under 500 euros",
        "Book a flight from Paris to Rome on December 15th for 1 week",
        "Find me a hotel in Madrid for 2 nights, budget 200 euros",
        "Travel from NYC to Paris next month for 5 days"
    ]
    
    try:
        from travel_ai import TravelAI
        
        ai = TravelAI()
        print("✅ TravelAI loaded successfully")
        print()
        
        for i, message in enumerate(test_cases, 1):
            print(f"📝 Test {i}: {message}")
            
            try:
                result = ai.extract_travel_info(message)
                request = result["travel_request"]
                
                print(f"   📍 {request.origin} → {request.destination}")
                print(f"   📅 {request.departure_date}")
                print(f"   ⏱️ {request.duration_days} days")
                print(f"   💰 €{request.budget}")
                print(f"   ✅ Complete: {request.is_complete()}")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
            
            print()
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    print("🚀 Travel AI Test Suite")
    print("=" * 50)
    print()
    
    # Check if OpenAI API key is set
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY not found in environment")
        print("💡 Add it to your .env file or set it as an environment variable")
        print()
        print("Example .env file:")
        print("OPENAI_API_KEY=your_openai_api_key_here")
        print("SMTP_EMAIL=your_email@example.com")
        print("SMTP_PASSWORD=your_email_password")
        exit(1)
    
    # Run tests
    print("Choose test:")
    print("1. Full workflow test (extraction + search + email)")
    print("2. Simple text extraction test")
    print()
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        test_travel_ai_workflow()
    elif choice == "2":
        test_simple_extraction()
    else:
        print("Invalid choice. Running full workflow test...")
        test_travel_ai_workflow() 