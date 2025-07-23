"""
Email Service - Send travel booking confirmations via Gmail
Step 7: Send final travel package to customer via email
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from models import TravelRequest, TravelPackage
from config import config
from gmail_auth import GmailAuthService


class EmailService:
    """Service for sending travel booking emails"""
    
    def __init__(self):
        # Try Gmail OAuth first, fallback to SMTP
        self.gmail_auth = GmailAuthService()
        self.use_oauth = False
        
        # Check if Gmail OAuth is available
        if self.gmail_auth.is_authenticated() or self._try_gmail_auth():
            self.use_oauth = True
            print("✅ Using Gmail OAuth for email sending")
        else:
            # Fallback to SMTP configuration
            email_config = config.get_email_config()
            self.smtp_server = email_config['smtp_server']
            self.smtp_port = email_config['smtp_port']
            self.email = email_config['email']
            self.password = email_config['password']
            print("⚠️ Using SMTP fallback for email sending")
    
    def _try_gmail_auth(self) -> bool:
        """Try to authenticate with Gmail OAuth silently"""
        try:
            return self.gmail_auth.authenticate()
        except Exception:
            return False
    
    def send_travel_package(self, request: TravelRequest, package: Optional[TravelPackage]) -> bool:
        """
        Step 7: Send final travel package to customer via Gmail
        """
        
        # Create email content
        subject = f"🎉 Your Perfect Trip: {request.origin} → {request.destination}"
        body = self._create_email_body(request, package)
        
        # Try Gmail OAuth first
        if self.use_oauth:
            try:
                # Ensure user_email is set from OAuth if not provided
                if not request.user_email and self.gmail_auth.get_user_email():
                    request.user_email = self.gmail_auth.get_user_email()
                
                success = self.gmail_auth.send_email(
                    to_email=request.user_email,
                    subject=subject,
                    html_body=body
                )
                
                if success:
                    print(f"✅ Travel package sent via Gmail OAuth to {request.user_email}")
                    return True
                else:
                    print("⚠️ Gmail OAuth failed, trying SMTP fallback...")
                    
            except Exception as e:
                print(f"⚠️ Gmail OAuth error: {e}, trying SMTP fallback...")
        
        # Fallback to SMTP
        if hasattr(self, 'email') and hasattr(self, 'password') and self.email and self.password:
            try:
                # Create message
                msg = MIMEMultipart()
                msg['From'] = self.email
                msg['To'] = request.user_email
                msg['Subject'] = subject
                
                msg.attach(MIMEText(body, 'html'))
                
                # Send email
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.email, self.password)
                    server.send_message(msg)
                
                print(f"✅ Travel package sent via SMTP to {request.user_email}")
                return True
                
            except Exception as e:
                print(f"❌ SMTP email failed: {e}")
        
        # If all methods fail, print to console
        print("⚠️ No email method available, printing email content instead:")
        self._print_email_content(request, package)
        return True
    
    def _create_email_body(self, request: TravelRequest, package: Optional[TravelPackage]) -> str:
        """Create HTML email body with travel package details"""
        
        if not package:
            return self._create_no_results_email(request)
        
        # Format dates
        departure_str = request.departure_date.strftime('%B %d, %Y')
        return_str = request.return_date.strftime('%B %d, %Y') if request.return_date else "One way"
        
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9f9f9;">
            <div style="background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #2c3e50; margin: 0;">✈️ Your Perfect Trip Package</h1>
                    <p style="color: #7f8c8d; font-size: 18px; margin: 10px 0;">Ready to book your adventure!</p>
                </div>
                
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; text-align: center;">
                    <h2 style="margin: 0; font-size: 24px;">{request.origin} → {request.destination}</h2>
                    <p style="margin: 10px 0 0 0; font-size: 16px;">{departure_str} to {return_str}</p>
                </div>
                
                {self._format_flight_section(package.flight) if package.flight else ''}
                
                {self._format_accommodation_section(package.accommodation) if package.accommodation else ''}
                
                <div style="background-color: #27ae60; color: white; padding: 20px; border-radius: 8px; text-align: center; margin: 25px 0;">
                    <h3 style="margin: 0; font-size: 24px;">💰 Total Package Price</h3>
                    <p style="margin: 10px 0 0 0; font-size: 32px; font-weight: bold;">€{package.total_price:.2f}</p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{self._get_booking_url(package)}" 
                       style="background-color: #e74c3c; color: white; padding: 15px 40px; text-decoration: none; border-radius: 25px; font-size: 18px; font-weight: bold; display: inline-block;">
                        🚀 BOOK NOW
                    </a>
                </div>
                
                <div style="background-color: #ecf0f1; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h4 style="color: #2c3e50; margin-top: 0;">📋 Your Trip Summary</h4>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px 0; font-weight: bold; color: #34495e;">Travelers:</td>
                            <td style="padding: 8px 0;">{request.passengers} {"person" if request.passengers == 1 else "people"}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; font-weight: bold; color: #34495e;">Duration:</td>
                            <td style="padding: 8px 0;">{request.duration_days or "Not specified"} days</td>
                        </tr>
                        {f'<tr><td style="padding: 8px 0; font-weight: bold; color: #34495e;">Budget:</td><td style="padding: 8px 0;">€{request.budget}</td></tr>' if request.budget else ''}
                    </table>
                </div>
                
                <div style="border-top: 2px solid #ecf0f1; padding-top: 20px; margin-top: 30px; text-align: center;">
                    <p style="color: #7f8c8d; font-size: 14px; margin: 0;">
                        <strong>Ready to book?</strong> Click the button above to secure your trip!<br>
                        Prices are subject to availability and may change.
                    </p>
                </div>
                
                <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ecf0f1;">
                    <p style="color: #95a5a6; font-size: 12px; margin: 0;">
                        Safe travels! ✈️<br>
                        <strong>Your AI Travel Assistant</strong><br>
                        <em>sayitsorted.com</em>
                    </p>
                </div>
                
            </div>
        </body>
        </html>
        """
    
    def _format_flight_section(self, flight) -> str:
        """Format flight details section"""
        return f"""
        <div style="border: 2px solid #3498db; border-radius: 8px; padding: 20px; margin: 20px 0;">
            <h3 style="color: #3498db; margin-top: 0; display: flex; align-items: center;">
                ✈️ Your Flight
            </h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 8px 0; font-weight: bold; color: #2c3e50;">Airline:</td>
                    <td style="padding: 8px 0;">{flight.airline} {flight.flight_number}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; font-weight: bold; color: #2c3e50;">Departure:</td>
                    <td style="padding: 8px 0;">{flight.departure_time}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; font-weight: bold; color: #2c3e50;">Arrival:</td>
                    <td style="padding: 8px 0;">{flight.arrival_time}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; font-weight: bold; color: #2c3e50;">Duration:</td>
                    <td style="padding: 8px 0;">{flight.duration}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; font-weight: bold; color: #2c3e50;">Type:</td>
                    <td style="padding: 8px 0;">{"✈️ Direct Flight" if flight.stops == 0 else f"{flight.stops} stop(s)"}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; font-weight: bold; color: #2c3e50;">Price:</td>
                    <td style="padding: 8px 0; font-size: 18px; font-weight: bold; color: #e74c3c;">€{flight.price}</td>
                </tr>
            </table>
        </div>
        """
    
    def _format_accommodation_section(self, accommodation) -> str:
        """Format accommodation details section"""
        return f"""
        <div style="border: 2px solid #e67e22; border-radius: 8px; padding: 20px; margin: 20px 0;">
            <h3 style="color: #e67e22; margin-top: 0; display: flex; align-items: center;">
                🏨 Your Accommodation
            </h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 8px 0; font-weight: bold; color: #2c3e50;">Hotel:</td>
                    <td style="padding: 8px 0;">{accommodation.name}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; font-weight: bold; color: #2c3e50;">Type:</td>
                    <td style="padding: 8px 0;">{accommodation.type.title()}</td>
                </tr>
                {f'<tr><td style="padding: 8px 0; font-weight: bold; color: #2c3e50;">Rating:</td><td style="padding: 8px 0;">⭐ {accommodation.rating}/5</td></tr>' if accommodation.rating else ''}
                <tr>
                    <td style="padding: 8px 0; font-weight: bold; color: #2c3e50;">Price per night:</td>
                    <td style="padding: 8px 0;">€{accommodation.price_per_night:.2f}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; font-weight: bold; color: #2c3e50;">Total accommodation:</td>
                    <td style="padding: 8px 0; font-size: 18px; font-weight: bold; color: #e74c3c;">€{accommodation.total_price:.2f}</td>
                </tr>
                {f'<tr><td style="padding: 8px 0; font-weight: bold; color: #2c3e50;">Amenities:</td><td style="padding: 8px 0;">{", ".join(accommodation.amenities)}</td></tr>' if accommodation.amenities else ''}
            </table>
        </div>
        """
    
    def _create_no_results_email(self, request: TravelRequest) -> str:
        """Create email when no travel package is found"""
        departure_str = request.departure_date.strftime('%B %d, %Y')
        
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: white; padding: 30px; border-radius: 10px;">
                <h2 style="color: #e74c3c;">😔 No Travel Options Found</h2>
                
                <p>Hi there!</p>
                <p>I searched for travel options from <strong>{request.origin}</strong> to <strong>{request.destination}</strong> 
                on <strong>{departure_str}</strong>, but unfortunately couldn't find any packages that match your criteria.</p>
                
                <h3>Your Search Criteria:</h3>
                <ul>
                    <li><strong>Route:</strong> {request.origin} → {request.destination}</li>
                    <li><strong>Date:</strong> {departure_str}</li>
                    <li><strong>Travelers:</strong> {request.passengers}</li>
                    {f'<li><strong>Budget:</strong> €{request.budget}</li>' if request.budget else ''}
                    {f'<li><strong>Duration:</strong> {request.duration_days} days</li>' if request.duration_days else ''}
                </ul>
                
                <p>Try adjusting your search criteria or check back later for new options.</p>
                
                <p>Best regards,<br>
                Your AI Travel Assistant</p>
            </div>
        </body>
        </html>
        """
    
    def _get_booking_url(self, package: TravelPackage) -> str:
        """Get booking URL - for now return flight booking URL"""
        if package.flight and package.flight.booking_url:
            return package.flight.booking_url
        elif package.accommodation and package.accommodation.booking_url:
            return package.accommodation.booking_url
        else:
            return "https://www.kiwi.com"  # Default booking platform
    
    def _print_email_content(self, request: TravelRequest, package: Optional[TravelPackage]):
        """Print email content to console when SMTP is not configured"""
        print("\n" + "="*60)
        print("📧 EMAIL CONTENT (SMTP not configured)")
        print("="*60)
        print(f"To: {request.user_email}")
        print(f"Subject: 🎉 Your Perfect Trip: {request.origin} → {request.destination}")
        print("-"*60)
        
        if package:
            print("✈️ TRAVEL PACKAGE FOUND!")
            print(f"Route: {request.origin} → {request.destination}")
            print(f"Date: {request.departure_date.strftime('%B %d, %Y')}")
            
            if package.flight:
                print(f"\n✈️ Flight: {package.flight.airline} {package.flight.flight_number}")
                print(f"   Time: {package.flight.departure_time} → {package.flight.arrival_time}")
                print(f"   Price: €{package.flight.price}")
            
            if package.accommodation:
                print(f"\n🏨 Hotel: {package.accommodation.name}")
                print(f"   Price: €{package.accommodation.price_per_night}/night")
                print(f"   Total: €{package.accommodation.total_price}")
            
            print(f"\n💰 TOTAL PACKAGE: €{package.total_price}")
            print(f"🚀 Booking URL: {self._get_booking_url(package)}")
        else:
            print("❌ No travel package found matching your criteria")
        
        print("="*60)
        print("📧 END EMAIL CONTENT")
        print("="*60 + "\n") 