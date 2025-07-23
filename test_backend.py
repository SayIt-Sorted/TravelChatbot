#!/usr/bin/env python3
"""
Simple test script to check backend startup
"""

import os
import sys

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        from travel_ai import TravelAI
        print("✅ TravelAI imported")
    except Exception as e:
        print(f"❌ TravelAI import failed: {e}")
        return False
    
    try:
        from search_service import SearchService
        print("✅ SearchService imported")
    except Exception as e:
        print(f"❌ SearchService import failed: {e}")
        return False
    
    try:
        from email_service import EmailService
        print("✅ EmailService imported")
    except Exception as e:
        print(f"❌ EmailService import failed: {e}")
        return False
    
    try:
        from models import TravelRequest
        print("✅ TravelRequest imported")
    except Exception as e:
        print(f"❌ TravelRequest import failed: {e}")
        return False
    
    try:
        from config import config
        print("✅ Config imported")
    except Exception as e:
        print(f"❌ Config import failed: {e}")
        return False
    
    return True

def test_config():
    """Test configuration"""
    print("\n🔍 Testing configuration...")
    
    try:
        from config import config
        
        # Check OpenAI API key
        openai_key = config.get_openai_api_key()
        if openai_key:
            print("✅ OpenAI API key found")
        else:
            print("⚠️ OpenAI API key not found - will use mock responses")
        
        # Check other configs
        print("✅ Configuration loaded successfully")
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_api_creation():
    """Test if the API can be created"""
    print("\n🔍 Testing API creation...")
    
    try:
        from main import app
        print("✅ FastAPI app created successfully")
        return True
    except Exception as e:
        print(f"❌ API creation failed: {e}")
        return False

def main():
    print("🚀 Backend Startup Test")
    print("=" * 40)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed")
        return False
    
    # Test configuration
    if not test_config():
        print("\n❌ Configuration tests failed")
        return False
    
    # Test API creation
    if not test_api_creation():
        print("\n❌ API creation failed")
        return False
    
    print("\n✅ All tests passed! Backend should start successfully.")
    print("\n💡 To start the backend:")
    print("   python main.py")
    print("   # or")
    print("   python -m uvicorn main:app --host 0.0.0.0 --port 8000")
    
    return True

if __name__ == "__main__":
    main() 