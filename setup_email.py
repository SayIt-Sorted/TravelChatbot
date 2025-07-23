#!/usr/bin/env python3
"""
Email Configuration Setup Script
Helps you set up email credentials for the travel chatbot
"""

import os
from pathlib import Path

def setup_email():
    """Set up email configuration"""
    print("📧 Email Configuration Setup")
    print("=" * 40)
    print("This will help you set up email sending for your travel chatbot.")
    print()
    
    # Check if .env exists
    env_file = Path('.env')
    if env_file.exists():
        print("✅ .env file already exists")
        if input("Do you want to update email configuration? (y/N): ").lower() != 'y':
            print("Skipping email setup.")
            return
    else:
        print("📝 Creating .env file...")
    
    print()
    print("🔧 Email Configuration")
    print("-" * 20)
    
    # Get email settings
    email = input("Enter your email address (e.g., joao@sayitsorted.com): ").strip()
    if not email:
        print("❌ Email address is required!")
        return
    
    password = input("Enter your SMTP password: ").strip()
    if not password:
        print("❌ SMTP password is required!")
        return
    
    # Create or update .env file
    env_content = f"""# Email Configuration (Hostinger SMTP)
SMTP_EMAIL={email}
SMTP_PASSWORD={password}

# OpenAI API Key
OPENAI_API_KEY={os.getenv('OPENAI_API_KEY', 'your_openai_api_key_here')}

# Optional: Flight Search API (Amadeus)
# AMADEUS_API_KEY=your_amadeus_api_key_here
# AMADEUS_API_SECRET=your_amadeus_api_secret_here
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ .env file created/updated successfully!")
        print()
        print("📧 Email Configuration Summary:")
        print(f"   Email: {email}")
        print(f"   SMTP Server: smtp.hostinger.com")
        print(f"   SMTP Port: 465 (SSL)")
        print()
        print("💡 Next steps:")
        print("   1. Make sure your Hostinger SMTP password is correct")
        print("   2. Test the email sending with: python test_travel_ai.py")
        print("   3. Deploy to Vercel with these environment variables")
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")

if __name__ == "__main__":
    setup_email() 