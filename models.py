"""
Data models for the Travel Booking Platform
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
from enum import Enum


class TravelRequest(BaseModel):
    """Main travel request containing all trip information"""
    # Basic trip info
    origin: Optional[str] = Field(None, description="Departure city")
    destination: Optional[str] = Field(None, description="Destination city")  
    departure_date: Optional[date] = Field(None, description="Check-in/departure date")
    return_date: Optional[date] = Field(None, description="Check-out/return date")
    duration_days: Optional[int] = Field(None, description="Trip duration in days")
    
    # Traveler info
    passengers: int = Field(1, description="Number of travelers")
    user_email: Optional[str] = Field(None, description="User email for booking confirmation")
    
    # Preferences
    budget: Optional[float] = Field(None, description="Total budget in EUR")
    
    def is_complete(self) -> bool:
        """Check if all required fields are filled"""
        return all([
            self.origin,
            self.destination, 
            self.departure_date,
            self.user_email
        ])
    
    def missing_fields(self) -> List[str]:
        """Return list of missing required fields"""
        missing = []
        if not self.origin:
            missing.append("origin")
        if not self.destination:
            missing.append("destination")
        if not self.departure_date:
            missing.append("departure_date")
        if not self.user_email:
            missing.append("user_email")
        return missing


class FlightOption(BaseModel):
    """Flight search result"""
    airline: str
    flight_number: str
    departure_time: str
    arrival_time: str
    duration: str
    price: float
    currency: str = "EUR"
    stops: int = 0
    booking_url: Optional[str] = None


class AccommodationOption(BaseModel):
    """Accommodation search result"""
    name: str
    type: str  # hotel, apartment, hostel, etc.
    rating: Optional[float] = None
    price_per_night: float
    total_price: float
    currency: str = "EUR"
    amenities: List[str] = []
    booking_url: Optional[str] = None


class TravelPackage(BaseModel):
    """Complete travel package with flight and accommodation"""
    flight: Optional[FlightOption] = None
    accommodation: Optional[AccommodationOption] = None
    total_price: float
    currency: str = "EUR"
    
    def format_summary(self) -> str:
        """Format package for display"""
        summary = []
        
        if self.flight:
            summary.append(f"✈️ Flight: {self.flight.airline} {self.flight.flight_number}")
            summary.append(f"   {self.flight.departure_time} → {self.flight.arrival_time}")
            summary.append(f"   €{self.flight.price}")
        
        if self.accommodation:
            summary.append(f"🏨 Hotel: {self.accommodation.name}")
            summary.append(f"   €{self.accommodation.price_per_night}/night")
            summary.append(f"   Total: €{self.accommodation.total_price}")
        
        summary.append(f"💰 Total Package: €{self.total_price}")
        
        return "\n".join(summary)
    
    def to_dict(self) -> dict:
        """Convert package to dictionary for API response"""
        return {
            "flight": self.flight.dict() if self.flight else None,
            "accommodation": self.accommodation.dict() if self.accommodation else None,
            "total_price": self.total_price,
            "currency": self.currency
        } 