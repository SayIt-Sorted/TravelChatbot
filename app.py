"""
Travel Booking AI - Main Application
Simple, modular, and scalable travel booking platform for remote workers

Steps implemented:
0. Customer logs in via Gmail OAuth for secure email access
2. Text analysis for key information extraction (GPT API)  
3. Follow-up questions via GPT API until all information is retrieved
5. Search for best flights + accommodation using Amadeus API (1 option each)
7. Send final package to customer via Gmail
"""

from typing import Dict, Any
from models import TravelRequest
from travel_ai import TravelAI
from search_service import SearchService
from email_service import EmailService
from gmail_auth import GmailAuthService
from config import config


class TravelBookingAI:
    """Main travel booking AI application"""
    
    def __init__(self):
        self.ai = TravelAI()
        self.search = SearchService()
        self.email = EmailService()
        self.gmail_auth = GmailAuthService()
        self.sessions: Dict[str, TravelRequest] = {}
        
        print("🤖 Travel Booking AI initialized!")
        print("I help remote workers book complete trips with flights + accommodation.")
        print("Just tell me where you want to go!\n")
    
    def process_message(self, user_id: str, message: str) -> str:
        """
        Main processing pipeline:
        Step 2: Extract travel information using AI
        Step 3: Ask follow-up questions if needed
        Step 5: Search for best travel package when complete
        Step 7: Send package via email
        """
        
        # Get current session
        current_request = self.sessions.get(user_id)
        
        # Step 2 & 3: Extract information and generate follow-up questions
        ai_result = self.ai.extract_travel_info(message, current_request)
        
        # Auto-fill email if user is logged in with Gmail OAuth
        if self.gmail_auth.is_authenticated() and not ai_result["travel_request"].user_email:
            ai_result["travel_request"].user_email = self.gmail_auth.get_user_email()
        
        # Update session
        self.sessions[user_id] = ai_result["travel_request"]
        
        # Check if we have all required information
        if ai_result["is_complete"] and ai_result["travel_request"].is_complete():
            return self._handle_complete_request(user_id, ai_result["travel_request"])
        else:
            # Step 3: Return follow-up question
            follow_up = ai_result.get("follow_up_question")
            if not follow_up:
                follow_up = self.ai.generate_follow_up_question(ai_result["travel_request"])
            return follow_up
    
    def _handle_complete_request(self, user_id: str, request: TravelRequest) -> str:
        """Handle complete travel request"""
        
        print(f"\n🔍 Searching for travel package...")
        print(f"Route: {request.origin} → {request.destination}")
        print(f"Date: {request.departure_date}")
        print(f"Duration: {request.duration_days} days" if request.duration_days else "Duration: Not specified")
        print(f"Travelers: {request.passengers}")
        print(f"Budget: €{request.budget}" if request.budget else "Budget: No limit")
        print(f"Email: {request.user_email}\n")
        
        # Step 5: Search for best travel package (flight + accommodation)
        package = self.search.search_best_package(request)
        
        # Step 7: Send package via email
        email_sent = self.email.send_travel_package(request, package)
        
        # Clear session
        if user_id in self.sessions:
            del self.sessions[user_id]
        
        # Return response to user
        if package:
            response = f"""
🎉 Perfect! I found a great travel package for you:

{package.format_summary()}

📧 I've sent the complete details with booking links to {request.user_email}

Ready to plan another trip? Just tell me where you'd like to go next!
            """
        else:
            response = f"""
😔 I couldn't find any travel packages matching your criteria:

📍 Route: {request.origin} → {request.destination}
📅 Date: {request.departure_date.strftime('%B %d, %Y')}
👥 Travelers: {request.passengers}
{f'💰 Budget: €{request.budget}' if request.budget else ''}

📧 I've sent this information to {request.user_email}

Try adjusting your criteria or different dates. Want to search again?
            """
        
        return response.strip()
    
    def run_interactive(self):
        """Run the AI in interactive mode for testing"""
        user_id = "demo_user"
        
        print("💬 Start chatting! Try something like:")
        print('   "Book a trip from Porto to London next weekend for 3 days under 500 euros"')
        print('   "I want to go from NYC to Paris on December 15th for a week"')
        print('   "Find me a flight and hotel from Madrid to Rome"')
        print()
        print("💡 Commands:")
        print("   'login' - Login with Gmail OAuth")
        print("   'logout' - Logout from Gmail")
        print("   'quit' or 'exit' - End the conversation")
        print("   'clear' - Clear current session")
        print()
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("\n✈️ Travel AI: Safe travels! Thanks for using our service!")
                    break
                
                if user_input.lower() == 'clear':
                    if user_id in self.sessions:
                        del self.sessions[user_id]
                    print("🗑️ Session cleared!")
                    continue
                
                if user_input.lower() == 'login':
                    if self.gmail_auth.authenticate():
                        print(f"✅ Logged in as: {self.gmail_auth.get_user_email()}")
                        # Reinitialize email service to use OAuth
                        self.email = EmailService()
                    else:
                        print("❌ Gmail login failed")
                    continue
                
                if user_input.lower() == 'logout':
                    if self.gmail_auth.logout():
                        # Reinitialize email service to fallback to SMTP
                        self.email = EmailService()
                    continue
                
                if not user_input:
                    continue
                
                response = self.process_message(user_id, user_input)
                print(f"\n🤖 Travel AI: {response}\n")
                
            except KeyboardInterrupt:
                print("\n\n✈️ Travel AI: Goodbye! Safe travels!")
                break
            except Exception as e:
                print(f"\n❌ Sorry, I encountered an error: {e}")
                print("Please try again.\n")


def check_configuration():
    """Check if configuration is properly set up"""
    print("🔧 Configuration Check")
    print("=" * 40)
    
    # Check OpenAI API key
    if not config.get_openai_api_key():
        print("❌ OpenAI API key is required!")
        print("Set OPENAI_API_KEY in your .env file")
        return False
    
    # Show configuration status
    config.print_status()
    
    print("\n✅ Configuration looks good!")
    return True


def main():
    """Main entry point"""
    
    print("🚀 Travel Booking AI for Remote Workers")
    print("=" * 50)
    
    # Check configuration
    if not check_configuration():
        print("\n📝 Setup Instructions:")
        print("1. Create .env file with OpenAI API key:")
        print("""
# OpenAI API (Required)
OPENAI_API_KEY=your_openai_api_key_here

# SMTP Email (Optional - Gmail OAuth is preferred)
SMTP_EMAIL=your_email@example.com
SMTP_PASSWORD=your_email_password_here

# Amadeus API (Optional - uses mock data without it)
AMADEUS_API_KEY=your_amadeus_api_key_here
AMADEUS_API_SECRET=your_amadeus_api_secret_here
        """)
        print("2. For best email experience, set up Gmail OAuth:")
        print("   Run: python gmail_auth.py")
        print("3. Then run: python app.py")
        return
    
    # Initialize and run the AI
    ai = TravelBookingAI()
    ai.run_interactive()


if __name__ == "__main__":
    main() 