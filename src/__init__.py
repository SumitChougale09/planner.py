# AI Trip Planner Package
from .config import TripPreferences, TripItinerary, ItineraryItem, AgentType, RoutingStrategy
from .agents.orchestrator import TripPlannerOrchestrator
from .routing import AdvancedRouter
from .services import MultilingualSupport, RealTimeUpdates, PaymentIntegration

__version__ = "1.0.0"
__author__ = "AI Trip Planner Team"

__all__ = [
    "TripPreferences",
    "TripItinerary", 
    "ItineraryItem",
    "AgentType",
    "RoutingStrategy",
    "TripPlannerOrchestrator",
    "AdvancedRouter",
    "MultilingualSupport",
    "RealTimeUpdates",
    "PaymentIntegration"
]
