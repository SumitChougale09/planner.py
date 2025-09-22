# Configuration and Data Models for AI Trip Planner
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from typing import List, Optional

@dataclass
class TripPreferences:
    budget: float
    duration_days: int
    interests: List[str]  # ['heritage', 'adventure', 'nightlife', 'culture', 'nature']
    location: str
    start_date: datetime
    travelers: int
    accommodation_type: str = "hotel"
    transport_preference: str = "mixed"
    language: str = "english"

@dataclass
class ItineraryItem:
    day: int
    time: str
    activity: str
    location: str
    cost: float
    duration_hours: float
    category: str
    booking_url: Optional[str] = None
    coordinates: Optional[tuple] = None

@dataclass
class TripItinerary:
    id: str
    preferences: TripPreferences
    items: List[ItineraryItem]
    total_cost: float
    created_at: datetime
    status: str = "draft"
    optimization_suggestions: Optional[List[str]] = None

class AgentType(Enum):
    ORCHESTRATOR = "orchestrator"
    RESEARCH = "research"
    PLANNING = "planning" 
    BOOKING = "booking"
    OPTIMIZATION = "optimization"
    MONITORING = "monitoring"

class RoutingStrategy(Enum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    SEMANTIC = "semantic"
    PRIORITY = "priority"
    FEEDBACK = "feedback"