"""
Gmail OAuth Authentication Service
Step 0: Customer logs in via Gmail OAuth for secure email access
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


class GmailAuthService:
    """Gmail OAuth authentication and email sending service"""
    
    # Gmail API scopes needed
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    
    def __init__(self, credentials_file: str = 'credentials.json', token_file: str = 'token.json'):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None
        self.user_email = None
    
    def setup_oauth_credentials(self) -> bool:
        """
        Guide user through OAuth setup process
        Returns True if credentials are properly configured
        """
        
        if not os.path.exists(self.credentials_file):
            print("❌ Gmail OAuth credentials not found!")
            print("\n📝 To set up Gmail OAuth:")
            print("1. Go to: https://console.cloud.google.com/")
            print("2. Create a new project or select existing one")
            print("3. Enable Gmail API")
            print("4. Go to 'Credentials' > 'Create Credentials' > 'OAuth 2.0 Client IDs'")
            print("5. Choose 'Desktop application'")
            print("6. Download the JSON file and save as 'credentials.json'")
            print("7. Run this app again")
            return False
        
        return True
    
    def authenticate(self) -> bool:
        """
        Authenticate user with Gmail OAuth
        Returns True if authentication successful
        """
        
        if not self.setup_oauth_credentials():
            return False
        
        creds = None
        
        # Load existing token if available
        if os.path.exists(self.token_file):
            try:
                creds = Credentials.from_authorized_user_file(self.token_file, self.SCOPES)
            except Exception as e:
                print(f"⚠️ Error loading existing token: {e}")
        
        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    print("✅ Gmail token refreshed successfully")
                except Exception as e:
                    print(f"⚠️ Token refresh failed: {e}")
                    creds = None
            
            if not creds:
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, self.SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                    print("✅ Gmail OAuth authentication successful!")
                except Exception as e:
                    print(f"❌ OAuth authentication failed: {e}")
                    return False
            
            # Save credentials for next run
            try:
                with open(self.token_file, 'w') as token:
                    token.write(creds.to_json())
                print("✅ Gmail credentials saved")
            except Exception as e:
                print(f"⚠️ Could not save credentials: {e}")
        
        # Build Gmail service
        try:
            self.service = build('gmail', 'v1', credentials=creds)
            
            # Get user email address
            profile = self.service.users().getProfile(userId='me').execute()
            self.user_email = profile.get('emailAddress')
            
            print(f"✅ Gmail authenticated as: {self.user_email}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to build Gmail service: {e}")
            return False
    
    def send_email(self, to_email: str, subject: str, html_body: str) -> bool:
        """
        Send email using authenticated Gmail account
        """
        
        if not self.service:
            print("❌ Gmail not authenticated. Call authenticate() first.")
            return False
        
        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['To'] = to_email
            message['From'] = self.user_email
            message['Subject'] = subject
            
            # Add HTML body
            html_part = MIMEText(html_body, 'html')
            message.attach(html_part)
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            # Send email
            send_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            print(f"✅ Email sent successfully to {to_email}")
            print(f"   Message ID: {send_message['id']}")
            return True
            
        except HttpError as error:
            print(f"❌ Gmail API error: {error}")
            return False
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False
    
    def is_authenticated(self) -> bool:
        """Check if user is currently authenticated"""
        return self.service is not None and self.user_email is not None
    
    def get_user_email(self) -> Optional[str]:
        """Get the authenticated user's email address"""
        return self.user_email
    
    def logout(self) -> bool:
        """Logout and clear stored credentials"""
        try:
            if os.path.exists(self.token_file):
                os.remove(self.token_file)
            self.service = None
            self.user_email = None
            print("✅ Logged out successfully")
            return True
        except Exception as e:
            print(f"❌ Logout failed: {e}")
            return False


def setup_gmail_oauth():
    """
    Interactive setup helper for Gmail OAuth
    """
    print("🔐 Gmail OAuth Setup")
    print("=" * 40)
    
    gmail_auth = GmailAuthService()
    
    if gmail_auth.authenticate():
        print("\n✅ Gmail OAuth setup complete!")
        print(f"Authenticated as: {gmail_auth.get_user_email()}")
        
        # Test email sending
        test_email = input(f"\nSend test email to {gmail_auth.get_user_email()}? (y/N): ")
        if test_email.lower() == 'y':
            success = gmail_auth.send_email(
                to_email=gmail_auth.get_user_email(),
                subject="🎉 Travel AI - Gmail OAuth Test",
                html_body="""
                <html>
                <body style="font-family: Arial, sans-serif; padding: 20px;">
                    <h2 style="color: #2c3e50;">🎉 Gmail OAuth Working!</h2>
                    <p>Congratulations! Your Travel Booking AI can now send emails through Gmail OAuth.</p>
                    <p>This test email confirms that:</p>
                    <ul>
                        <li>✅ OAuth authentication is working</li>
                        <li>✅ Gmail API access is granted</li>
                        <li>✅ Email sending is functional</li>
                    </ul>
                    <p>You're ready to start booking trips! 🚀</p>
                    <hr>
                    <p style="color: #7f8c8d; font-size: 12px;">
                        Sent by Travel Booking AI<br>
                        <em>sayitsorted.com</em>
                    </p>
                </body>
                </html>
                """
            )
            
            if success:
                print("✅ Test email sent! Check your inbox.")
            else:
                print("❌ Test email failed.")
        
        return True
    else:
        print("\n❌ Gmail OAuth setup failed.")
        return False


if __name__ == "__main__":
    setup_gmail_oauth() 