#!/usr/bin/env python3
"""
Simple test for the Travel Booking AI
"""

from models import TravelRequest
from travel_ai import TravelAI
from search_service import SearchService
from email_service import EmailService
from gmail_auth import GmailAuthService
from datetime import date, timedelta


def test_models():
    """Test the data models"""
    print("🧪 Testing Models...")
    
    # Test TravelRequest
    request = TravelRequest(
        origin="Porto",
        destination="London", 
        departure_date=date.today() + timedelta(days=7),
        passengers=2,
        budget=500.0,
        user_email="test@example.com"
    )
    
    print(f"✅ TravelRequest created: {request.origin} → {request.destination}")
    print(f"   Complete: {request.is_complete()}")
    print(f"   Missing: {request.missing_fields()}")


def test_search_service():
    """Test the search service with mock data"""
    print("\n🧪 Testing Search Service...")
    
    search = SearchService()
    
    request = TravelRequest(
        origin="Porto",
        destination="London",
        departure_date=date.today() + timedelta(days=7),
        duration_days=3,
        passengers=1,
        budget=400.0,
        user_email="test@example.com"
    )
    
    package = search.search_best_package(request)
    
    if package:
        print("✅ Search service working!")
        print(f"   Flight: {package.flight.airline if package.flight else 'None'}")
        print(f"   Hotel: {package.accommodation.name if package.accommodation else 'None'}")
        print(f"   Total: €{package.total_price}")
    else:
        print("❌ Search service failed")


def test_email_service():
    """Test email service (will print to console)"""
    print("\n🧪 Testing Email Service...")
    
    email = EmailService()
    
    request = TravelRequest(
        origin="Porto",
        destination="London",
        departure_date=date.today() + timedelta(days=7),
        duration_days=3,
        passengers=1,
        user_email="test@example.com"
    )
    
    # Create a mock package
    from models import FlightOption, AccommodationOption, TravelPackage
    
    flight = FlightOption(
        airline="TAP Air Portugal",
        flight_number="TP1234",
        departure_time="08:30",
        arrival_time="11:45",
        duration="3h 15m",
        price=156.99,
        stops=0
    )
    
    accommodation = AccommodationOption(
        name="Hotel Central London",
        type="hotel",
        rating=4.2,
        price_per_night=89.00,
        total_price=267.00
    )
    
    package = TravelPackage(
        flight=flight,
        accommodation=accommodation,
        total_price=423.99
    )
    
    result = email.send_travel_package(request, package)
    print(f"✅ Email service {'working' if result else 'failed'}")


def test_gmail_oauth():
    """Test Gmail OAuth authentication"""
    print("\n🧪 Testing Gmail OAuth...")
    
    gmail_auth = GmailAuthService()
    
    if gmail_auth.is_authenticated():
        print("✅ Gmail OAuth already authenticated!")
        print(f"   User: {gmail_auth.get_user_email()}")
    else:
        print("⚠️ Gmail OAuth not authenticated")
        print("   Run 'python gmail_auth.py' to set up")


def main():
    print("🧪 Travel Booking AI - Simple Tests")
    print("=" * 40)
    
    try:
        test_models()
        test_search_service()
        test_email_service()
        test_gmail_oauth()
        
        print("\n✅ All tests completed!")
        print("\n💡 Next steps:")
        print("1. Set up Gmail OAuth: python gmail_auth.py")
        print("2. Run the app: python app.py")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("💡 Check your .env file and dependencies")


if __name__ == "__main__":
    main() 