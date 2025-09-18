class PlanningAgent:
    """Agent specialized in creating itineraries"""
    
    def __init__(self, llm):
        self.llm = llm
        
    async def arun(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create detailed itinerary"""
        preferences = context.get('preferences')
        research_data = context.get('previous_results', {}).get('research', {})
        
        if not preferences:
            return {"error": "No preferences provided"}
        
        # Mock itinerary creation
        itinerary = []
        for day in range(1, preferences.duration_days + 1):
            daily_activities = self._plan_daily_activities(day, preferences, research_data)
            itinerary.extend(daily_activities)
        
        return {
            "itinerary": itinerary,
            "total_estimated_cost": preferences.budget * 0.8,
            "schedule_optimized": True
        }
    
    def _plan_daily_activities(self, day: int, preferences: TripPreferences, research_data: Dict) -> List[ItineraryItem]:
        """Plan activities for a specific day"""
        activities = []
        
        # Morning activity
        activities.append(ItineraryItem(
            day=day,
            time="09:00",
            activity=f"Morning {preferences.interests[0] if preferences.interests else 'sightseeing'}",
            location=preferences.location,
            cost=preferences.budget / preferences.duration_days * 0.3,
            duration_hours=3,
            category=preferences.interests[0] if preferences.interests else "general"
        ))
        
        # Afternoon activity
        activities.append(ItineraryItem(
            day=day,
            time="14:00",
            activity=f"Afternoon {preferences.interests[1] if len(preferences.interests) > 1 else 'exploration'}",
            location=preferences.location,
            cost=preferences.budget / preferences.duration_days * 0.4,
            duration_hours=4,
            category=preferences.interests[1] if len(preferences.interests) > 1 else "general"
        ))
        
        return activities