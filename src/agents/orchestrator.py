# Trip Planner Orchestrator
import uuid
from datetime import datetime
from typing import Dict, Any
import json
from datetime import datetime, timedelta

import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory

from src.config import TripPreferences, TripItinerary, RoutingStrategy
from src.routing import AdvancedRouter
from src.agents.research_agent import ResearchAgent
from src.agents.planning_agent import PlanningAgent
from src.agents.optimization_agent import OptimizationAgent
from src.agents.booking_agent import BookingAgent
from src.agents.monitoring_agent import MonitoringAgent


class TripPlannerOrchestrator:
    """Main orchestrator managing the entire trip planning workflow"""
    
    def __init__(self, gemini_api_key: str):
        # Initialize Gemini LLM
        genai.configure(api_key=gemini_api_key)
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.3,
            google_api_key=gemini_api_key
        )
        
        # Initialize router and agents
        self.router = AdvancedRouter(self.llm)
        self.agents = self._initialize_agents()
        self.memory = ConversationBufferMemory(return_messages=True)
        
    def _initialize_agents(self) -> Dict[str, Any]:
        """Initialize all specialized agents"""
        return {
            "research": ResearchAgent(self.llm),
            "planning": PlanningAgent(self.llm),
            "optimization": OptimizationAgent(self.llm),
            "booking": BookingAgent(self.llm),
            "monitoring": MonitoringAgent(self.llm)
        }
    
    async def plan_trip_from_prompt(self, prompt: str, routing_strategy: RoutingStrategy = RoutingStrategy.SEQUENTIAL) -> TripItinerary:
        """Parses a natural language prompt, creates preferences, and then plans a trip."""
        print(f"\n🤖 Parsing prompt: '{prompt}'")
        
        # Use the LLM to extract structured data from the prompt
        extraction_prompt = f"""
        You are a travel planning assistant. Extract the trip details from the following prompt and format them as a JSON object.
        User Prompt: "{prompt}"

        Extract the following fields:
        - budget (float)
        - duration_days (int)
        - interests (list of strings)
        - location (string)
        - start_date (string, YYYY-MM-DD format)
        - travelers (int)

        If a value isn't specified, use a sensible default. For the start_date, if not mentioned, assume it's 30 days from today's date: {datetime.now().date()}.
        """
        
        response = await self.llm.ainvoke(extraction_prompt)
        extracted_text = response.content.strip().replace('`json', '').replace('`', '')
        
        try:
            trip_data = json.loads(extracted_text)
            print(f"✅ Extracted Trip Data: {trip_data}")
            
            preferences = TripPreferences(
                budget=float(trip_data.get('budget', 50000.0)),
                duration_days=int(trip_data.get('duration_days', 5)),
                interests=list(trip_data.get('interests', ['culture'])),
                location=str(trip_data.get('location', 'not specified')),
                start_date=datetime.strptime(trip_data.get('start_date'), '%Y-%m-%d'),
                travelers=int(trip_data.get('travelers', 2))
            )
            
            # Once preferences are created, call the main planning method
            return await self.plan_trip(preferences, routing_strategy)
            
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print(f"❌ Error parsing prompt: {e}")
            # Fallback or error handling
            return None

    async def plan_trip(self, preferences: TripPreferences, routing_strategy: RoutingStrategy = RoutingStrategy.SEQUENTIAL) -> TripItinerary:
        """Main entry point for trip planning"""
        context = {
            'preferences': preferences,
            'user_input': f"Plan a trip to {preferences.location} for {preferences.duration_days} days",
            'budget': preferences.budget,
            'duration_days': preferences.duration_days,
            'interests': preferences.interests,
            'location': preferences.location,
            'needs_info': True
        }
        
        # Execute routing strategy
        results = await self.router.route_by_strategy(routing_strategy, context, self.agents)
        
        # Process results into final itinerary
        itinerary = self._create_final_itinerary(preferences, results)
        
        return itinerary
    
    def _create_final_itinerary(self, preferences: TripPreferences, results: Dict[str, Any]) -> TripItinerary:
        """Combine all agent results into final itinerary"""
        # Safely get results from different agents
        planning_result = results.get('planning') or {}
        optimization_result = results.get('optimization') or {}
        
        items = planning_result.get('itinerary', [])
        initial_cost = planning_result.get('total_cost', 0)

        cost_savings = optimization_result.get('cost_savings', 0)
        suggestions = optimization_result.get('suggestions', [])

        final_cost = initial_cost - cost_savings
        
        return TripItinerary(
            id=f"TRIP_{uuid.uuid4().hex[:8]}",
            preferences=preferences,
            items=items,
            total_cost=final_cost,
            created_at=datetime.now(),
            status="planned",
            optimization_suggestions=suggestions
        )
    
    async def adaptive_replan(self, itinerary: TripItinerary, changes: Dict[str, Any]) -> TripItinerary:
        """Adaptively replan based on real-time changes"""
        context = {
            'existing_itinerary': itinerary,
            'changes': changes,
            'preferences': itinerary.preferences
        }
        
        # Use feedback routing for adaptive changes
        results = await self.router.route_by_strategy(RoutingStrategy.FEEDBACK, context, self.agents)
        
        # Update itinerary
        updated_itinerary = self._create_final_itinerary(itinerary.preferences, results)
        updated_itinerary.status = "updated"
        
        return updated_itinerary