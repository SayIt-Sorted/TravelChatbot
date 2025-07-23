"""
Travel AI Service - Handles conversation and information extraction
Steps 2 & 3: Text analysis and follow-up questions using GPT
"""

import json
from typing import Dict, Any, Optional
from datetime import datetime, date
import openai
from models import TravelRequest
from config import config


class TravelAI:
    """AI service for travel conversation and information extraction"""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=config.get_openai_api_key())
        self.model = config.get('openai.model', 'gpt-3.5-turbo')
        self.temperature = config.get('openai.temperature', 0.1)
    
    def extract_travel_info(self, user_message: str, current_request: Optional[TravelRequest] = None) -> Dict[str, Any]:
        """
        Step 2: Extract travel information from user message
        Step 3: Generate follow-up questions if information is missing
        """
        
        # Prepare current context
        current_info = {}
        if current_request:
            current_info = {
                "origin": current_request.origin,
                "destination": current_request.destination,
                "departure_date": current_request.departure_date.isoformat() if current_request.departure_date else None,
                "return_date": current_request.return_date.isoformat() if current_request.return_date else None,
                "duration_days": current_request.duration_days,
                "passengers": current_request.passengers,
                "budget": current_request.budget,
                "user_email": current_request.user_email
            }
        
        system_prompt = f"""You are a travel booking assistant. Extract travel information from user messages and ask follow-up questions when needed.

Current trip information: {json.dumps(current_info, indent=2)}

From the user's message, extract:
1. origin (departure city)
2. destination (arrival city)  
3. departure_date (YYYY-MM-DD format)
4. return_date (YYYY-MM-DD format, optional)
5. duration_days (number of days)
6. passengers (number of travelers)
7. budget (total budget in EUR)
8. user_email (email address)

Rules:
- Only extract information that is explicitly mentioned or clearly implied
- For dates, convert relative terms like "next Friday", "this weekend" to actual dates
- If duration is mentioned but no return date, calculate return_date
- If return date is mentioned but no duration, calculate duration_days
- Don't make assumptions about missing information

Respond with JSON in this exact format:
{{
  "extracted_info": {{
    "origin": "city name or null",
    "destination": "city name or null", 
    "departure_date": "YYYY-MM-DD or null",
    "return_date": "YYYY-MM-DD or null",
    "duration_days": number or null,
    "passengers": number or null,
    "budget": number or null,
    "user_email": "email or null"
  }},
  "is_complete": true/false,
  "missing_fields": ["field1", "field2"],
  "follow_up_question": "question to ask user or null",
  "confidence": 0.0-1.0
}}

Today's date: {date.today().isoformat()}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ]
            )
            
            # Parse the JSON response
            content = response.choices[0].message.content.strip()
            if content.startswith('```json'):
                content = content[7:-3].strip()
            elif content.startswith('```'):
                content = content[3:-3].strip()
            
            result = json.loads(content)
            
            # Update current request with extracted info
            updated_request = self._update_request(current_request or TravelRequest(), result["extracted_info"])
            
            return {
                "travel_request": updated_request,
                "extracted_info": result["extracted_info"],
                "is_complete": result.get("is_complete", False),
                "follow_up_question": result.get("follow_up_question"),
                "confidence": result.get("confidence", 0.8),
                "missing_fields": result.get("missing_fields", [])
            }
            
        except Exception as e:
            print(f"❌ AI extraction error: {e}")
            return {
                "travel_request": current_request or TravelRequest(),
                "is_complete": False,
                "follow_up_question": "I'm sorry, I didn't understand that. Could you please tell me where you'd like to travel from and to?",
                "confidence": 0.0,
                "missing_fields": ["origin", "destination", "departure_date", "user_email"]
            }
    
    def _update_request(self, current_request: TravelRequest, extracted_info: Dict[str, Any]) -> TravelRequest:
        """Update travel request with extracted information"""
        
        # Create a dict of current values
        update_data = current_request.model_dump()
        
        # Update with extracted information (only if not None)
        for key, value in extracted_info.items():
            if value is not None:
                if key in ["departure_date", "return_date"] and isinstance(value, str):
                    try:
                        update_data[key] = datetime.strptime(value, "%Y-%m-%d").date()
                    except ValueError:
                        continue
                else:
                    update_data[key] = value
        
        # Calculate missing fields if possible
        if update_data.get("departure_date") and update_data.get("duration_days") and not update_data.get("return_date"):
            departure = update_data["departure_date"]
            if isinstance(departure, str):
                departure = datetime.strptime(departure, "%Y-%m-%d").date()
            from datetime import timedelta
            update_data["return_date"] = departure + timedelta(days=update_data["duration_days"])
        
        elif update_data.get("departure_date") and update_data.get("return_date") and not update_data.get("duration_days"):
            departure = update_data["departure_date"]
            return_date = update_data["return_date"]
            if isinstance(departure, str):
                departure = datetime.strptime(departure, "%Y-%m-%d").date()
            if isinstance(return_date, str):
                return_date = datetime.strptime(return_date, "%Y-%m-%d").date()
            update_data["duration_days"] = (return_date - departure).days
        
        return TravelRequest(**update_data)
    
    def generate_follow_up_question(self, travel_request: TravelRequest) -> str:
        """Generate a natural follow-up question for missing information"""
        
        missing = travel_request.missing_fields()
        
        if not missing:
            return "Great! I have all the information I need. Let me search for the best options for you."
        
        # Prioritize questions
        if "origin" in missing:
            return "Where would you like to travel from?"
        elif "destination" in missing:
            return "Where would you like to go?"
        elif "departure_date" in missing:
            return "When would you like to depart?"
        elif "user_email" in missing:
            return "What's your email address so I can send you the booking details?"
        else:
            # Ask about optional fields
            if not travel_request.return_date and not travel_request.duration_days:
                return "How long would you like to stay? (e.g., '3 days' or 'return on Friday')"
            elif travel_request.passengers == 1:
                return "How many travelers will there be?"
            elif not travel_request.budget:
                return "Do you have a budget in mind for this trip?"
        
        return "Is there anything else you'd like to specify for your trip?" 