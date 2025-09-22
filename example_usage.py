#!/usr/bin/env python3
"""
Example usage of the modular AI Trip Planner system.
This demonstrates how to use the different components independently.
"""

import asyncio
from datetime import datetime, timedelta

# Import from the modular structure
from src.config import TripPreferences, RoutingStrategy
from src.agents.orchestrator import TripPlannerOrchestrator
from src.services import MultilingualSupport, PaymentIntegration


async def example_basic_usage():
    """Example of basic trip planning usage"""
    print("=== Basic Trip Planning Example ===")
    
    # Initialize orchestrator (replace with your actual API key)
    GEMINI_API_KEY = "your_gemini_api_key_here"
    orchestrator = TripPlannerOrchestrator(GEMINI_API_KEY)
    
    # Create trip preferences
    preferences = TripPreferences(
        budget=75000.0,
        duration_days=7,
        interests=['heritage', 'adventure', 'culture'],
        location='Kerala, India',
        start_date=datetime.now() + timedelta(days=45),
        travelers=3,
        language='english'
    )
    
    # Plan trip with sequential routing
    itinerary = await orchestrator.plan_trip(
        preferences, 
        RoutingStrategy.SEQUENTIAL
    )
    
    print(f"✅ Trip planned: {itinerary.id}")
    print(f"   Destination: {itinerary.preferences.location}")
    print(f"   Duration: {itinerary.preferences.duration_days} days")
    print(f"   Total cost: ₹{itinerary.total_cost:,.2f}")
    print(f"   Activities: {len(itinerary.items)}")
    
    return itinerary


async def example_routing_strategies():
    """Example of different routing strategies"""
    print("\n=== Routing Strategies Example ===")
    
    GEMINI_API_KEY = "your_gemini_api_key_here"
    orchestrator = TripPlannerOrchestrator(GEMINI_API_KEY)
    
    preferences = TripPreferences(
        budget=30000.0,
        duration_days=3,
        interests=['nature', 'photography'],
        location='Himachal Pradesh, India',
        start_date=datetime.now() + timedelta(days=15),
        travelers=2
    )
    
    strategies = [
        RoutingStrategy.SEQUENTIAL,
        RoutingStrategy.CONDITIONAL,
        RoutingStrategy.PRIORITY
    ]
    
    for strategy in strategies:
        print(f"\n🔄 Testing {strategy.value.upper()} routing:")
        try:
            itinerary = await orchestrator.plan_trip(preferences, strategy)
            print(f"   ✅ Success: {itinerary.id} - ₹{itinerary.total_cost:,.2f}")
        except Exception as e:
            print(f"   ❌ Error: {e}")


async def example_services():
    """Example of using additional services"""
    print("\n=== Services Example ===")
    
    # Create a sample itinerary for demonstration
    preferences = TripPreferences(
        budget=40000.0,
        duration_days=4,
        interests=['culture', 'food'],
        location='Tamil Nadu, India',
        start_date=datetime.now() + timedelta(days=20),
        travelers=2
    )
    
    # Initialize services
    multilingual = MultilingualSupport(None)  # In real usage, pass LLM
    payment = PaymentIntegration()
    
    # Example: Translate itinerary
    print("🌐 Multilingual Support:")
    # Note: This is a mock implementation
    print("   Supported languages: english, hindi, tamil, bengali, marathi")
    
    # Example: Payment processing
    print("\n💳 Payment Integration:")
    payment_result = await payment.process_payment(25000.0, {"method": "card"})
    print(f"   Payment status: {payment_result['status']}")
    print(f"   Transaction ID: {payment_result['transaction_id']}")


async def example_adaptive_replanning():
    """Example of adaptive replanning"""
    print("\n=== Adaptive Replanning Example ===")
    
    GEMINI_API_KEY = "your_gemini_api_key_here"
    orchestrator = TripPlannerOrchestrator(GEMINI_API_KEY)
    
    # Create initial trip
    preferences = TripPreferences(
        budget=60000.0,
        duration_days=5,
        interests=['heritage', 'shopping'],
        location='Delhi, India',
        start_date=datetime.now() + timedelta(days=30),
        travelers=2
    )
    
    # Plan initial trip
    itinerary = await orchestrator.plan_trip(preferences)
    print(f"📋 Initial trip: {itinerary.id} - ₹{itinerary.total_cost:,.2f}")
    
    # Simulate changes
    changes = {
        'weather_change': True,
        'budget_increase': 15000,
        'new_interest': 'adventure',
        'duration_extension': 2
    }
    
    # Replan with changes
    updated_itinerary = await orchestrator.adaptive_replan(itinerary, changes)
    print(f"🔄 Updated trip: {updated_itinerary.id} - ₹{updated_itinerary.total_cost:,.2f}")
    print(f"   Status: {updated_itinerary.status}")


async def main():
    """Main example function"""
    print("🚀 AI Trip Planner - Modular Usage Examples")
    print("=" * 50)
    
    try:
        # Run examples
        await example_basic_usage()
        await example_routing_strategies()
        await example_services()
        await example_adaptive_replanning()
        
        print("\n" + "=" * 50)
        print("🎉 All examples completed successfully!")
        print("\nKey Benefits of Modular Structure:")
        print("   ✓ Clean separation of concerns")
        print("   ✓ Easy to import specific components")
        print("   ✓ Simple to extend and maintain")
        print("   ✓ Better testability")
        print("   ✓ Professional code organization")
        
    except Exception as e:
        print(f"❌ Error running examples: {e}")
        print("\nNote: Make sure to set your GEMINI_API_KEY in the script")


if __name__ == "__main__":
    # Run the examples
    asyncio.run(main())
