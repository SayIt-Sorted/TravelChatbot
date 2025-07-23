#!/usr/bin/env python3
"""
Simple Email Configuration Test
Tests if your email settings are working correctly
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_email_config():
    """Test email configuration"""
    print("📧 Testing Email Configuration")
    print("=" * 40)
    
    # Check environment variables
    email = os.getenv('SMTP_EMAIL')
    password = os.getenv('SMTP_PASSWORD')
    
    if not email:
        print("❌ SMTP_EMAIL not found in .env file")
        print("💡 Run: python setup_email.py")
        return False
    
    if not password:
        print("❌ SMTP_PASSWORD not found in .env file")
        print("💡 Run: python setup_email.py")
        return False
    
    print(f"✅ Email: {email}")
    print(f"✅ Password: {'*' * len(password)} (configured)")
    print(f"✅ SMTP Server: smtp.hostinger.com")
    print(f"✅ SMTP Port: 465 (SSL)")
    print()
    
    # Test email service
    try:
        from email_service import EmailService
        from models import TravelRequest, TravelPackage, FlightOption, AccommodationOption
        
        print("🔍 Testing EmailService...")
        email_service = EmailService()
        
        # Create a test travel request
        from datetime import date
        test_request = TravelRequest(
            origin="Porto",
            destination="London",
            departure_date=date(2025, 7, 26),
            return_date=date(2025, 7, 29),
            duration_days=3,
            passengers=1,
            budget=500.0,
            user_email="joaopaesteves99@gmail.com"
        )
        
        # Create a test package
        test_flight = FlightOption(
            airline="TAP Air Portugal",
            flight_number="TP1234",
            departure_time="08:30",
            arrival_time="11:45",
            duration="3h 15m",
            price=89.99,
            currency="EUR",
            stops=0,
            booking_url="https://www.flytap.com/booking/12345"
        )
        
        test_accommodation = AccommodationOption(
            name="Hotel Central London",
            type="hotel",
            rating=4.2,
            price_per_night=65.0,
            total_price=195.0,
            currency="EUR",
            amenities=["WiFi", "Breakfast", "City Center"],
            booking_url="https://www.booking.com/hotel/example"
        )
        
        test_package = TravelPackage(
            flight=test_flight,
            accommodation=test_accommodation,
            total_price=284.99,
            currency="EUR"
        )
        
        print("📧 Attempting to send test email...")
        result = email_service.send_travel_package(test_request, test_package)
        
        if result:
            print("✅ Email test completed!")
            print("💡 Check your email inbox for the test message")
        else:
            print("❌ Email test failed")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Email test error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_email_config() 