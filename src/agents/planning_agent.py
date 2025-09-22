# Planning Agent for AI Trip Planner
import json
from typing import Dict, Any, List
from ..config import TripPreferences, ItineraryItem

class PlanningAgent:
    """Agent specialized in creating itineraries using LLM reasoning."""
    
    def __init__(self, llm):
        self.llm = llm
        
    async def arun(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create a detailed itinerary by reasoning over research data."""
        preferences = context.get('preferences')
        research_results = context.get('previous_results', {}).get('research', {})
        points_of_interest = research_results.get('points_of_interest', [])
        
        if not preferences:
            return {"error": "No preferences provided"}
        
        if not points_of_interest:
            return {"error": "No points of interest found to create a plan"}

        print(" Planning agent is creating an itinerary...")

        # Create a detailed prompt for the LLM
        prompt = self._create_planning_prompt(preferences, points_of_interest)
        
        # Invoke the LLM
        response = await self.llm.ainvoke(prompt)
        llm_output = response.content.strip().replace('`json', '').replace('`', '')

        # Parse the LLM's JSON response
        try:
            itinerary_data = json.loads(llm_output)
            itinerary_items = [
                ItineraryItem(**item) for item in itinerary_data.get('itinerary', [])
            ]
            total_cost = sum(item.cost for item in itinerary_items)
            
            print(f" Planning agent finished. Itinerary created with {len(itinerary_items)} items.")
            
            return {
                "itinerary": itinerary_items,
                "total_cost": total_cost
            }
        except (json.JSONDecodeError, TypeError) as e:
            print(f" Error parsing itinerary from LLM: {e}")
            print(f"LLM Output was: {llm_output}")
            return {"error": "Failed to parse the itinerary plan from the LLM."}

    def _create_planning_prompt(self, preferences: TripPreferences, pois: List[Dict[str, Any]]) -> str:
        """Creates a sophisticated prompt for the LLM to generate an itinerary."""
        pois_text = "\n".join([f"- {poi['name']} (Type: {poi['type']}, Location: {poi['lat']},{poi['lon']})" for poi in pois])

        prompt = f"""
You are an expert travel planner. Your task is to create a personalized, day-by-day itinerary based on the user's preferences and a list of available points of interest.

**User Preferences:**
- **Destination:** {preferences.location}
- **Duration:** {preferences.duration_days} days
- **Budget:** Approximately {preferences.budget} INR total
- **Interests:** {', '.join(preferences.interests)}
- **Travelers:** {preferences.travelers}

**Available Points of Interest:**
{pois_text}

**Instructions:**
1.  Create a logical and enjoyable itinerary for the entire duration of {preferences.duration_days} days.
2.  Select the most relevant points of interest from the list provided that match the user's interests.
3.  Schedule 2-3 activities per day. Do not overpack the schedule. Leave time for travel and relaxation.
4.  Estimate a realistic cost in INR for each activity for {preferences.travelers} people.
5.  Ensure the total estimated cost of all activities does not exceed the user's total budget of {preferences.budget} INR.
6.  Structure your output as a single JSON object with a key called "itinerary". The value should be a list of JSON objects, where each object represents one activity and has the following keys:
    - `day` (integer): The day of the activity (e.g., 1, 2).
    - `time` (string): The suggested time for the activity (e.g., "09:00", "14:30").
    - `activity` (string): The name of the activity or place to visit.
    - `location` (string): The name of the location (can be the same as the activity).
    - `cost` (float): The estimated cost for this activity in INR.
    - `duration_hours` (float): The estimated duration of the activity in hours.
    - `category` (string): The category of the activity (e.g., 'culture', 'nightlife', 'beach').

**Example of a single item in the itinerary list:**
{{
    "day": 1,
    "time": "10:00",
    "activity": "Visit the City Palace",
    "location": "City Palace, Udaipur",
    "cost": 1000.0,
    "duration_hours": 3.0,
    "category": "heritage"
}}

Now, generate the complete JSON output for the itinerary.
"""
        return prompt