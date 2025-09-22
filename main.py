# AI-Powered Trip Planner with Advanced Agent Routing
# This system demonstrates comprehensive routing patterns for AI agents

import asyncio
from datetime import datetime, timedelta

# Import from modular structure
from src.config import TripPreferences, RoutingStrategy, TripItinerary
from src.agents.orchestrator import TripPlannerOrchestrator


def display_itinerary(itinerary: TripItinerary):
    """Formats and displays the trip itinerary in a readable way."""
    print("\n" + "="*50)
    print(f"✈️ Trip Itinerary: {itinerary.id} ✈️")
    print(f"Status: {itinerary.status.title()}")
    print(f"Destination: {itinerary.preferences.location}")
    print(f"Duration: {itinerary.preferences.duration_days} days")
    print(f"Total Cost: ₹{itinerary.total_cost:,.2f}")
    print("="*50)

    if not itinerary.items:
        print("No items in this itinerary.")
        return

    # Group items by day
    items_by_day = {}
    for item in itinerary.items:
        if item.day not in items_by_day:
            items_by_day[item.day] = []
        items_by_day[item.day].append(item)

    for day in sorted(items_by_day.keys()):
        print(f"\n--- Day {day} ---")
        for item in sorted(items_by_day[day], key=lambda x: x.time):
            print(f"  🕒 {item.time}: {item.activity} ({item.category.title()})")
            print(f"     💰 Cost: ₹{item.cost:,.2f}")


async def demo_advanced_routing(orchestrator: TripPlannerOrchestrator):
    """Demonstrate the advanced routing system"""
    
    # Create sample trip preferences
    preferences = TripPreferences(
        budget=50000.0,
        duration_days=5,
        interests=['heritage', 'culture', 'nightlife'],
        location='Pune',
        start_date=datetime.now() + timedelta(days=30),
        travelers=2,
        language='english'
    )
    
    print("Starting AI Trip Planner Demo")
    print(f"Planning trip to {preferences.location} for {preferences.duration_days} days")
    print(f"Budget: ₹{preferences.budget:,.2f}")
    print(f"Interests: {', '.join(preferences.interests)}")
    print("\n" + "="*50)
    
    # Test different routing strategies
    strategies = [
        RoutingStrategy.SEQUENTIAL,
        # RoutingStrategy.CONDITIONAL,
        # RoutingStrategy.PRIORITY
    ]
    
    for strategy in strategies:
        print(f"\n🔄 Testing {strategy.value.upper()} routing:")
        try:
            itinerary = await orchestrator.plan_trip(preferences, strategy)
            display_itinerary(itinerary)
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
        display_itinerary(updated_itinerary)
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

async def demo_prompt_based_planning(orchestrator: TripPlannerOrchestrator):
    """Demonstrates planning from a natural language prompt."""
    print("\n" + "="*50)
    print("📝 Starting AI Trip Planner Demo from Prompt")
    
    # Example prompt
    prompt = "I want to plan a 7-day trip to Goa for 2 people. Our budget is around 80,000 INR and we are interested in beaches, nightlife, and local food."
    
    # Plan the trip using the new prompt-based method
    itinerary = await orchestrator.plan_trip_from_prompt(
        prompt,
        routing_strategy=RoutingStrategy.SEQUENTIAL
    )
    
    if itinerary:
        display_itinerary(itinerary)
        print(f"\n🎉 Prompt-based trip planned successfully!")
        print(f"   Itinerary ID: {itinerary.id}")
        print(f"   Destination: {itinerary.preferences.location}")
        print(f"   Final Cost: ₹{itinerary.total_cost:,.2f}")
    else:
        print("\n❌ Failed to plan the trip from the prompt.")

if __name__ == "__main__":
    # To run this demo, set your Gemini API key in the orchestrator initialization
    GEMINI_API_KEY = "AIzaSyATNVOYqxVVtnwJ0DKR0fmAWDCCtthG02E"  # IMPORTANT: Replace with your actual key
    orchestrator = TripPlannerOrchestrator(GEMINI_API_KEY)

    # Run both demos
    asyncio.run(demo_advanced_routing(orchestrator))
    #asyncio.run(demo_prompt_based_planning(orchestrator))