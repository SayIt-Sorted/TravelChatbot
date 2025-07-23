"""
Customer Gmail Login Service (Optional)
Step 0: Customer can optionally log in via Gmail to auto-fill their email
"""

import os
import json
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class CustomerGmailLogin:
    """Optional customer Gmail login for email auto-fill"""
    
    # Only need profile scope to get email address
    SCOPES = ['https://www.googleapis.com/auth/userinfo.email']
    
    def __init__(self, credentials_file: str = 'credentials.json', token_file: str = 'customer_token.json'):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None
        self.customer_email = None
    
    def is_setup_available(self) -> bool:
        """Check if OAuth credentials are available"""
        return os.path.exists(self.credentials_file)
    
    def customer_login(self) -> Optional[str]:
        """
        Let customer log in with their Gmail to auto-fill email
        Returns their email address if successful
        """
        
        if not self.is_setup_available():
            print("⚠️ Gmail login not available (no credentials.json)")
            return None
        
        creds = None
        
        # Load existing token if available
        if os.path.exists(self.token_file):
            try:
                creds = Credentials.from_authorized_user_file(self.token_file, self.SCOPES)
            except Exception:
                pass
        
        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception:
                    creds = None
            
            if not creds:
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, self.SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                except Exception as e:
                    print(f"❌ Gmail login failed: {e}")
                    return None
            
            # Save credentials for next time
            try:
                with open(self.token_file, 'w') as token:
                    token.write(creds.to_json())
            except Exception:
                pass
        
        # Get customer email
        try:
            from googleapiclient.discovery import build
            service = build('oauth2', 'v2', credentials=creds)
            user_info = service.userinfo().get().execute()
            self.customer_email = user_info.get('email')
            
            if self.customer_email:
                print(f"✅ Logged in as: {self.customer_email}")
                return self.customer_email
            else:
                print("❌ Could not get email from Gmail")
                return None
                
        except Exception as e:
            print(f"❌ Failed to get user info: {e}")
            return None
    
    def get_customer_email(self) -> Optional[str]:
        """Get the logged-in customer's email"""
        return self.customer_email
    
    def is_logged_in(self) -> bool:
        """Check if customer is logged in"""
        return self.customer_email is not None
    
    def logout(self) -> bool:
        """Logout customer"""
        try:
            if os.path.exists(self.token_file):
                os.remove(self.token_file)
            self.customer_email = None
            print("✅ Logged out successfully")
            return True
        except Exception:
            return False


def quick_setup_info():
    """Show quick setup info for Gmail login"""
    print("🔐 Optional: Customer Gmail Login Setup")
    print("=" * 45)
    print("This allows customers to login with Gmail to auto-fill their email.")
    print("It's completely optional - customers can just type their email instead.")
    print()
    print("To enable this feature:")
    print("1. Go to: https://console.cloud.google.com/")
    print("2. Create a project and enable 'Google+ API'")
    print("3. Create OAuth 2.0 credentials for 'Desktop application'")
    print("4. Download as 'credentials.json'")
    print("5. Customers can then use 'login' command in the app")
    print()
    print("💡 Without this, customers just type their email - works perfectly!")


if __name__ == "__main__":
    quick_setup_info() 