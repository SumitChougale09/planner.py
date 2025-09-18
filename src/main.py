# AI-Powered Trip Planner with Advanced Agent Routing
# This system demonstrates comprehensive routing patterns for AI agents

import os
import json
import asyncio
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
import logging

# Core LangChain imports
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools import BaseTool, tool
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain.memory import ConversationBufferMemory
from langchain.callbacks import BaseCallbackHandler
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema.runnable import Runnable, RunnablePassthrough, RunnableLambda
from langchain.schema.runnable.config import RunnableConfig

# Advanced routing imports
from langchain.schema.runnable import RunnableBranch, RunnableRouter
from langchain.utils.math import cosine_similarity
from langchain_core.runnables import RunnableParallel, RunnableSequence

# LLM imports (Gemini)
from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai

# Additional utilities
import numpy as np
from collections import defaultdict
import uuid
import aiohttp
import requests

# ===============================
# 1. CONFIGURATION & SETUP
# ===============================

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

# ===============================
# 2. ADVANCED ROUTING ENGINE
# ===============================

class AdvancedRouter:
    """
    Comprehensive routing system demonstrating multiple routing strategies
    """
    
    def __init__(self, llm):
        self.llm = llm
        self.routing_history = []
        self.agent_performance = defaultdict(list)
        self.semantic_embeddings = {}
        
    async def route_by_strategy(self, strategy: RoutingStrategy, context: Dict[str, Any], agents: Dict[str, Any]):
        """Main routing dispatcher"""
        routing_methods = {
            RoutingStrategy.SEQUENTIAL: self._sequential_routing,
            RoutingStrategy.PARALLEL: self._parallel_routing,
            RoutingStrategy.CONDITIONAL: self._conditional_routing,
            RoutingStrategy.SEMANTIC: self._semantic_routing,
            RoutingStrategy.PRIORITY: self._priority_routing,
            RoutingStrategy.FEEDBACK: self._feedback_routing
        }
        
        return await routing_methods[strategy](context, agents)
    
    async def _sequential_routing(self, context: Dict[str, Any], agents: Dict[str, Any]):
        """Execute agents in sequence with dependency management"""
        sequence = [
            AgentType.RESEARCH,
            AgentType.PLANNING,
            AgentType.OPTIMIZATION,
            AgentType.BOOKING
        ]
        
        results = {}
        for agent_type in sequence:
            if agent_type.value in agents:
                # Pass previous results as context
                context['previous_results'] = results
                result = await agents[agent_type.value].arun(context)
                results[agent_type.value] = result
                
        return results
    
    async def _parallel_routing(self, context: Dict[str, Any], agents: Dict[str, Any]):
        """Execute independent agents in parallel"""
        parallel_agents = [AgentType.RESEARCH, AgentType.MONITORING]
        
        tasks = []
        for agent_type in parallel_agents:
            if agent_type.value in agents:
                tasks.append(agents[agent_type.value].arun(context))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return dict(zip([a.value for a in parallel_agents], results))
    
    async def _conditional_routing(self, context: Dict[str, Any], agents: Dict[str, Any]):
        """Route based on conditions and business logic"""
        conditions = {
            'budget_high': context.get('budget', 0) > 100000,
            'duration_long': context.get('duration_days', 0) > 7,
            'complex_interests': len(context.get('interests', [])) > 3,
            'international': context.get('location', '').lower() not in ['india', 'domestic']
        }
        
        routing_rules = {
            'budget_high': [AgentType.RESEARCH, AgentType.PLANNING, AgentType.OPTIMIZATION],
            'duration_long': [AgentType.RESEARCH, AgentType.PLANNING, AgentType.MONITORING],
            'complex_interests': [AgentType.RESEARCH, AgentType.OPTIMIZATION],
            'default': [AgentType.RESEARCH, AgentType.PLANNING]
        }
        
        # Determine which rule to apply
        active_rule = 'default'
        for condition, is_met in conditions.items():
            if is_met and condition in routing_rules:
                active_rule = condition
                break
                
        selected_agents = routing_rules[active_rule]
        results = {}
        
        for agent_type in selected_agents:
            if agent_type.value in agents:
                result = await agents[agent_type.value].arun(context)
                results[agent_type.value] = result
                
        return results
    
    async def _semantic_routing(self, context: Dict[str, Any], agents: Dict[str, Any]):
        """Route based on semantic similarity of user intent"""
        user_query = context.get('user_input', '')
        
        # Agent capabilities (in real app, these would be learned embeddings)
        agent_capabilities = {
            'research': "find information about destinations, attractions, hotels, restaurants, local culture, weather, events",
            'planning': "create itineraries, schedule activities, organize timeline, plan routes, optimize sequences",
            'booking': "make reservations, handle payments, confirm bookings, manage tickets, process transactions",
            'optimization': "improve costs, enhance experiences, find alternatives, optimize routes, suggest upgrades"
        }
        
        # Simple semantic matching (in production, use proper embeddings)
        best_match = None
        best_score = 0
        
        for agent, capabilities in agent_capabilities.items():
            # Simplified similarity (in production, use sentence transformers)
            common_words = set(user_query.lower().split()) & set(capabilities.lower().split())
            score = len(common_words) / max(len(user_query.split()), 1)
            
            if score > best_score:
                best_score = score
                best_match = agent
                
        if best_match and best_match in agents:
            result = await agents[best_match].arun(context)
            return {best_match: result}
        
        return await self._sequential_routing(context, agents)
    
    async def _priority_routing(self, context: Dict[str, Any], agents: Dict[str, Any]):
        """Route based on agent priorities and current load"""
        # Priority scores based on context
        priorities = {
            AgentType.RESEARCH: self._calculate_priority('research', context),
            AgentType.PLANNING: self._calculate_priority('planning', context),
            AgentType.BOOKING: self._calculate_priority('booking', context),
            AgentType.OPTIMIZATION: self._calculate_priority('optimization', context)
        }
        
        # Sort agents by priority
        sorted_agents = sorted(priorities.items(), key=lambda x: x[1], reverse=True)
        
        results = {}
        for agent_type, priority in sorted_agents:
            if agent_type.value in agents and priority > 0.5:  # Threshold
                result = await agents[agent_type.value].arun(context)
                results[agent_type.value] = result
                
        return results
    
    async def _feedback_routing(self, context: Dict[str, Any], agents: Dict[str, Any]):
        """Route based on previous performance and feedback"""
        # Get performance history
        agent_scores = {}
        for agent_type in AgentType:
            if agent_type.value in agents:
                scores = self.agent_performance[agent_type.value]
                agent_scores[agent_type.value] = np.mean(scores) if scores else 0.5
        
        # Route to best performing agents first
        best_agents = sorted(agent_scores.items(), key=lambda x: x[1], reverse=True)[:2]
        
        results = {}
        for agent_name, score in best_agents:
            if score > 0.6:  # Performance threshold
                result = await agents[agent_name].arun(context)
                results[agent_name] = result
                
        return results
    
    def _calculate_priority(self, agent_type: str, context: Dict[str, Any]) -> float:
        """Calculate agent priority based on context"""
        base_priority = 0.5
        
        if agent_type == 'research':
            if context.get('needs_info', True):
                base_priority += 0.4
            if len(context.get('interests', [])) > 2:
                base_priority += 0.2
                
        elif agent_type == 'planning':
            if context.get('duration_days', 0) > 3:
                base_priority += 0.3
            if context.get('budget', 0) > 50000:
                base_priority += 0.2
                
        elif agent_type == 'booking':
            if context.get('ready_to_book', False):
                base_priority += 0.5
                
        elif agent_type == 'optimization':
            if context.get('budget', 0) < 20000:
                base_priority += 0.4
                
        return min(base_priority, 1.0)

# ===============================
# 3. SPECIALIZED AGENTS
# ===============================

class ResearchAgent:
    """Agent specialized in gathering travel information"""
    
    def __init__(self, llm):
        self.llm = llm
        self.tools = self._create_tools()
        
    def _create_tools(self):
        @tool
        def search_destinations(query: str) -> str:
            """Search for destination information, attractions, and local insights"""
            # Mock implementation - in production, integrate with real APIs
            return f"Found information about {query}: Popular attractions, local culture, weather conditions, and travel tips."
        
        @tool
        def get_weather_info(location: str, date: str) -> str:
            """Get weather information for a location and date"""
            return f"Weather for {location} on {date}: Pleasant conditions, 25°C average temperature."
        
        @tool
        def find_accommodations(location: str, budget: float, dates: str) -> str:
            """Find suitable accommodations within budget"""
            return f"Found accommodations in {location} within budget {budget}: Various options available."
        
        return [search_destinations, get_weather_info, find_accommodations]
    
    async def arun(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute research tasks"""
        preferences = context.get('preferences')
        if not preferences:
            return {"error": "No preferences provided"}
        
        research_results = {
            "destinations": f"Research completed for {preferences.location}",
            "attractions": f"Found attractions matching {preferences.interests}",
            "weather": "Weather information gathered",
            "accommodations": f"Accommodations within budget {preferences.budget} found"
        }
        
        return research_results

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

class OptimizationAgent:
    """Agent specialized in optimizing itineraries for cost and experience"""
    
    def __init__(self, llm):
        self.llm = llm
        
    async def arun(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize the itinerary"""
        planning_result = context.get('previous_results', {}).get('planning', {})
        preferences = context.get('preferences')
        
        if not planning_result or not preferences:
            return {"error": "No planning data to optimize"}
        
        optimization_results = {
            "cost_savings": preferences.budget * 0.15,
            "route_optimized": True,
            "alternative_suggestions": 3,
            "efficiency_score": 0.85
        }
        
        return optimization_results

class BookingAgent:
    """Agent specialized in handling bookings and payments"""
    
    def __init__(self, llm):
        self.llm = llm
        
    async def arun(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle booking process"""
        itinerary = context.get('previous_results', {}).get('planning', {})
        preferences = context.get('preferences')
        
        if not itinerary or not preferences:
            return {"error": "No itinerary to book"}
        
        booking_results = {
            "booking_status": "confirmed",
            "booking_ids": [f"BK{uuid.uuid4().hex[:8]}" for _ in range(3)],
            "payment_processed": True,
            "confirmation_sent": True
        }
        
        return booking_results

class MonitoringAgent:
    """Agent for real-time monitoring and adjustments"""
    
    def __init__(self, llm):
        self.llm = llm
        
    async def arun(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor trip conditions and suggest adjustments"""
        return {
            "weather_updates": "All clear",
            "traffic_conditions": "Normal",
            "alternative_routes": [],
            "last_updated": datetime.now().isoformat()
        }

# ===============================
# 4. ORCHESTRATION SYSTEM
# ===============================

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

# ===============================
# 5. ADVANCED FEATURES
# ===============================

class MultilingualSupport:
    """Handle multilingual interactions"""
    
    def __init__(self, llm):
        self.llm = llm
        self.supported_languages = ['english', 'hindi', 'tamil', 'bengali', 'marathi']
    
    async def translate_itinerary(self, itinerary: TripItinerary, target_language: str) -> TripItinerary:
        """Translate itinerary to target language"""
        # Mock translation - in production, integrate with translation API
        translated_itinerary = itinerary
        return translated_itinerary

class RealTimeUpdates:
    """Handle real-time updates and notifications"""
    
    def __init__(self):
        self.active_trips = {}
        self.update_handlers = []
    
    async def monitor_trip(self, itinerary_id: str):
        """Monitor trip for real-time updates"""
        # Mock monitoring - in production, integrate with real APIs
        updates = {
            "weather_alert": False,
            "traffic_delay": False,
            "booking_changes": False
        }
        return updates

class PaymentIntegration:
    """Handle payments and EMT inventory integration"""
    
    def __init__(self):
        self.payment_gateway = "mock_gateway"
        self.emt_integration = "mock_emt"
    
    async def process_payment(self, amount: float, payment_details: Dict[str, Any]) -> Dict[str, Any]:
        """Process payment through gateway"""
        return {
            "status": "success",
            "transaction_id": f"TXN_{uuid.uuid4().hex[:8]}",
            "amount": amount,
            "timestamp": datetime.now().isoformat()
        }
    
    async def book_through_emt(self, itinerary: TripItinerary) -> Dict[str, Any]:
        """Book through EMT inventory"""
        return {
            "booking_status": "confirmed",
            "emt_reference": f"EMT_{uuid.uuid4().hex[:8]}",
            "tickets_issued": len(itinerary.items)
        }

# ===============================
# 6. DEMO USAGE
# ===============================

async def demo_advanced_routing():
    """Demonstrate the advanced routing system"""
    
    # Initialize the orchestrator (you'll need to provide your Gemini API key)
    GEMINI_API_KEY = "your_gemini_api_key_here"  # Replace with actual key
    orchestrator = TripPlannerOrchestrator(GEMINI_API_KEY)
    
    # Create sample trip preferences
    preferences = TripPreferences(
        budget=50000.0,
        duration_days=5,
        interests=['heritage', 'culture', 'nightlife'],
        location='Rajasthan, India',
        start_date=datetime.now() + timedelta(days=30),
        travelers=2,
        language='english'
    )
    
    print("🚀 Starting AI Trip Planner Demo")
    print(f"Planning trip to {preferences.location} for {preferences.duration_days} days")
    print(f"Budget: ₹{preferences.budget:,.2f}")
    print(f"Interests: {', '.join(preferences.interests)}")
    print("\n" + "="*50)
    
    # Test different routing strategies
    strategies = [
        RoutingStrategy.SEQUENTIAL,
        RoutingStrategy.CONDITIONAL,
        RoutingStrategy.PRIORITY
    ]
    
    for strategy in strategies:
        print(f"\n🔄 Testing {strategy.value.upper()} routing:")
        try:
            itinerary = await orchestrator.plan_trip(preferences, strategy)
            print(f"✅ Trip planned successfully!")
            print(f"   Itinerary ID: {itinerary.id}")
            print(f"   Total activities: {len(itinerary.items)}")
            print(f"   Final cost: ₹{itinerary.total_cost:,.2f}")
            print(f"   Status: {itinerary.status}")
        except Exception as e:
            print(f"❌ Error with {strategy.value}: {e}")
    
    # Demonstrate adaptive replanning
    print(f"\n🔄 Testing adaptive replanning:")
    changes = {
        'weather_change': True,
        'budget_increase': 10000,
        'new_interest': 'adventure'
    }
    
    try:
        updated_itinerary = await orchestrator.adaptive_replan(itinerary, changes)
        print(f"✅ Trip replanned successfully!")
        print(f"   Updated cost: ₹{updated_itinerary.total_cost:,.2f}")
        print(f"   Status: {updated_itinerary.status}")
    except Exception as e:
        print(f"❌ Error in replanning: {e}")
    
    print("\n" + "="*50)
    print("🎉 Demo completed! The system demonstrates:")
    print("   ✓ Multi-agent orchestration")
    print("   ✓ Advanced routing strategies")
    print("   ✓ Dynamic replanning capabilities")
    print("   ✓ Extensible architecture")

if __name__ == "__main__":
    # Note: To run this demo, you'll need to:
    # 1. Install required packages: pip install langchain langchain-google-genai google-generativeai
    # 2. Set up your Gemini API key
    # 3. Run: python trip_planner.py
    
    print("AI Trip Planner with Advanced Routing")
    print("=====================================")
    print("\nTo run the demo:")
    print("1. Set your Gemini API key in the GEMINI_API_KEY variable")
    print("2. Install requirements: pip install langchain langchain-google-genai google-generativeai")
    print("3. Run: asyncio.run(demo_advanced_routing())")
    print("\nKey Features Demonstrated:")
    print("• Sequential, Parallel, Conditional routing")
    print("• Semantic and Priority-based routing")
    print("• Feedback-driven agent selection")
    print("• Multi-agent orchestration")
    print("• Real-time adaptation")
    print("• Payment and booking integration")