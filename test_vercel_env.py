#!/usr/bin/env python3
"""
Test to check environment variables in Vercel-like conditions
"""

import os
from dotenv import load_dotenv

def test_vercel_env():
    """Test environment variables like Vercel would see them"""
    print("🔍 Testing Environment Variables (Vercel-like)")
    print("=" * 50)
    
    # Check if we're in a Vercel-like environment
    is_vercel = os.getenv('VERCEL') or os.getenv('AWS_LAMBDA_FUNCTION_NAME')
    print(f"🌐 Environment: {'Vercel/Serverless' if is_vercel else 'Local'}")
    print()
    
    # Check email environment variables
    smtp_email = os.getenv('SMTP_EMAIL')
    smtp_password = os.getenv('SMTP_PASSWORD')
    
    print("📧 Email Configuration:")
    print(f"   SMTP_EMAIL: {'✅ Set' if smtp_email else '❌ Missing'}")
    print(f"   SMTP_PASSWORD: {'✅ Set' if smtp_password else '❌ Missing'}")
    
    if smtp_email:
        print(f"   Email: {smtp_email}")
    if smtp_password:
        print(f"   Password: {'*' * len(smtp_password)}")
    
    print()
    
    # Test email service initialization
    try:
        from email_service import EmailService
        email_service = EmailService()
        
        print("🔧 EmailService Configuration:")
        print(f"   SMTP Server: {email_service.smtp_server}")
        print(f"   SMTP Port: {email_service.smtp_port}")
        print(f"   Sender Email: {'✅ Set' if email_service.sender_email else '❌ Missing'}")
        print(f"   Sender Password: {'✅ Set' if email_service.sender_password else '❌ Missing'}")
        
        if email_service.sender_email and email_service.sender_password:
            print("✅ Email service is properly configured!")
        else:
            print("❌ Email service is missing credentials!")
            print("💡 Add SMTP_EMAIL and SMTP_PASSWORD to Vercel environment variables")
            
    except Exception as e:
        print(f"❌ Error testing email service: {e}")
    
    print()
    print("💡 If email credentials are missing, add them to Vercel:")
    print("   1. Go to Vercel Dashboard → Settings → Environment Variables")
    print("   2. Add SMTP_EMAIL and SMTP_PASSWORD")
    print("   3. Redeploy your API")

if __name__ == "__main__":
    test_vercel_env() 