class TripPlannerOrchestrator:
    """Main orchestrator managing the entire trip planning workflow"""
    
    def __init__(self, gemini_api_key: str):
        # Initialize Gemini LLM
        genai.configure(api_key=gemini_api_key)
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
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
        planning_result = results.get('planning', {})
        optimization_result = results.get('optimization', {})
        
        items = planning_result.get('itinerary', [])
        cost_savings = optimization_result.get('cost_savings', 0)
        total_cost = max(0, preferences.budget - cost_savings)
        
        return TripItinerary(
            id=f"TRIP_{uuid.uuid4().hex[:8]}",
            preferences=preferences,
            items=items,
            total_cost=total_cost,
            created_at=datetime.now(),
            status="planned"
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