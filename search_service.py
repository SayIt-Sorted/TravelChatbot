"""
Search Service - Handles flight and accommodation search
Step 5: Search for best flights and accommodations using Amadeus API
"""

import requests
from typing import List, Optional
from datetime import datetime, timedelta
from models import TravelRequest, FlightOption, AccommodationOption, TravelPackage
from config import config


class SearchService:
    """Service for searching flights and accommodations"""
    
    def __init__(self):
        flight_config = config.get_flight_search_config()
        self.api_key = flight_config.get('amadeus_api_key')
        self.api_secret = flight_config.get('amadeus_api_secret')
        self.base_url = "https://test.api.amadeus.com"
        self.access_token = None
        self.use_mock = flight_config.get('use_mock', True)
    
    def search_best_package(self, request: TravelRequest) -> Optional[TravelPackage]:
        """
        Step 5: Search for the best travel package (flight + accommodation)
        Returns only 1 best option as specified in requirements
        """
        
        # Quick budget check first
        if request.budget and request.budget < 100:
            print(f"⚠️ Budget €{request.budget} is too low for available options")
            return None
        
        if self.use_mock or not self._authenticate():
            return self._get_mock_package(request)
        
        # Search for flights
        flight = self._search_flight(request)
        
        # Search for accommodation  
        accommodation = self._search_accommodation(request)
        
        if not flight and not accommodation:
            return None
        
        # Calculate total price
        total_price = 0
        if flight:
            total_price += flight.price
        if accommodation:
            total_price += accommodation.total_price
        
        return TravelPackage(
            flight=flight,
            accommodation=accommodation,
            total_price=total_price
        )
    
    def _authenticate(self) -> bool:
        """Authenticate with Amadeus API"""
        if not self.api_key or not self.api_secret:
            return False
        
        try:
            response = requests.post(
                f"{self.base_url}/v1/security/oauth2/token",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.api_key,
                    "client_secret": self.api_secret
                },
                timeout=10  # 10 second timeout
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get("access_token")
                return True
            else:
                print(f"❌ Amadeus auth failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Amadeus auth error: {e}")
            return False
    
    def _search_flight(self, request: TravelRequest) -> Optional[FlightOption]:
        """Search for best flight option"""
        try:
            params = {
                "originLocationCode": self._get_airport_code(request.origin),
                "destinationLocationCode": self._get_airport_code(request.destination),
                "departureDate": request.departure_date.strftime("%Y-%m-%d"),
                "adults": request.passengers,
                "currencyCode": "EUR",
                "max": 1  # Only get 1 option as specified
            }
            
            if request.return_date:
                params["returnDate"] = request.return_date.strftime("%Y-%m-%d")
            
            response = requests.get(
                f"{self.base_url}/v2/shopping/flight-offers",
                headers={"Authorization": f"Bearer {self.access_token}"},
                params=params,
                timeout=10  # 10 second timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                flights = data.get("data", [])
                
                if flights:
                    flight_data = flights[0]  # Get the first (best) option
                    return self._parse_flight(flight_data, request)
            
            return None
            
        except Exception as e:
            print(f"❌ Flight search error: {e}")
            return None
    
    def _search_accommodation(self, request: TravelRequest) -> Optional[AccommodationOption]:
        """Search for best accommodation option"""
        # Note: Amadeus has hotel search API, but for MVP we'll use mock data
        # In production, integrate with Booking.com, Expedia, etc.
        return self._get_mock_accommodation(request)
    
    def _parse_flight(self, flight_data: dict, request: TravelRequest) -> FlightOption:
        """Parse Amadeus flight data into FlightOption"""
        try:
            itineraries = flight_data.get("itineraries", [])
            if not itineraries:
                return None
            
            outbound = itineraries[0]
            segments = outbound.get("segments", [])
            
            if not segments:
                return None
            
            first_segment = segments[0]
            last_segment = segments[-1]
            
            # Extract flight details
            carrier_code = first_segment.get("carrierCode", "XX")
            flight_number = first_segment.get("number", "0000")
            
            departure_time = first_segment.get("departure", {}).get("at", "")[-8:-3]
            arrival_time = last_segment.get("arrival", {}).get("at", "")[-8:-3]
            
            duration = outbound.get("duration", "PT2H0M")
            duration = duration.replace("PT", "").replace("H", "h ").replace("M", "m")
            
            price = float(flight_data.get("price", {}).get("total", 0))
            stops = len(segments) - 1
            
            # Apply budget filter
            if request.budget and price > request.budget:
                return None
            
            return FlightOption(
                airline=f"{carrier_code}",
                flight_number=f"{carrier_code}{flight_number}",
                departure_time=departure_time,
                arrival_time=arrival_time,
                duration=duration,
                price=price,
                stops=stops,
                booking_url=f"https://www.amadeus.com/flights?offer={flight_data.get('id', '')}"
            )
            
        except Exception as e:
            print(f"❌ Flight parsing error: {e}")
            return None
    
    def _get_airport_code(self, city: str) -> str:
        """Map city names to airport codes"""
        city_codes = {
            "porto": "OPO", "london": "LON", "paris": "PAR", "madrid": "MAD",
            "barcelona": "BCN", "rome": "ROM", "amsterdam": "AMS", "berlin": "BER",
            "new york": "NYC", "nyc": "NYC", "los angeles": "LAX", "lisbon": "LIS",
            "frankfurt": "FRA", "munich": "MUC", "milan": "MIL", "zurich": "ZRH",
            "vienna": "VIE", "prague": "PRG", "budapest": "BUD", "dublin": "DUB"
        }
        return city_codes.get(city.lower(), city.upper()[:3])
    
    def _get_mock_package(self, request: TravelRequest) -> TravelPackage:
        """Generate mock travel package for testing"""
        
        # Check budget immediately - if too low, return None quickly
        if request.budget and request.budget < 100:  # Minimum realistic budget
            print(f"⚠️ Budget €{request.budget} is too low for available options")
            return None
        
        # Mock flight with realistic pricing
        base_flight_price = 89.99  # More realistic base price
        flight = FlightOption(
            airline="TAP Air Portugal",
            flight_number="TP1234",
            departure_time="08:30",
            arrival_time="11:45",
            duration="3h 15m",
            price=base_flight_price,
            stops=0,
            booking_url="https://www.flytap.com/booking/12345"
        )
        
        # Mock accommodation with realistic pricing
        accommodation = self._get_mock_accommodation(request)
        
        # Calculate total price
        total_price = flight.price + (accommodation.total_price if accommodation else 0)
        
        # Apply budget constraint
        if request.budget and total_price > request.budget:
            print(f"⚠️ Total package €{total_price:.2f} exceeds budget €{request.budget}")
            return None
        
        return TravelPackage(
            flight=flight,
            accommodation=accommodation,
            total_price=total_price
        )
    
    def _get_mock_accommodation(self, request: TravelRequest) -> AccommodationOption:
        """Generate mock accommodation"""
        nights = request.duration_days or 3
        price_per_night = 65.00  # More realistic price
        
        return AccommodationOption(
            name=f"Hotel Central {request.destination}",
            type="hotel",
            rating=4.2,
            price_per_night=price_per_night,
            total_price=price_per_night * nights,
            amenities=["WiFi", "Breakfast", "City Center"],
            booking_url="https://www.booking.com/hotel/example"
        ) 