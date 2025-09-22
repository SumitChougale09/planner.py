# AI Trip Planner - Modular Architecture

A sophisticated AI-powered trip planning system with advanced agent routing patterns, now organized in a clean modular structure.

## 🏗️ Project Structure

```
src/
├── __init__.py                 # Package initialization and exports
├── config.py                   # Data models and configuration
├── routing.py                  # Advanced routing engine
├── services.py                 # Advanced services (multilingual, payments, etc.)
├── main.py                     # Demo and main execution
└── agents/
    ├── __init__.py             # Agents package initialization
    ├── research_agent.py       # Research and information gathering
    ├── planning_agent.py       # Itinerary creation and planning
    ├── optimization_agent.py   # Cost and experience optimization
    ├── booking_agent.py        # Booking and payment handling
    ├── monitoring_agent.py     # Real-time monitoring
    └── orchestrator.py         # Main orchestration system
```

## 🚀 Key Features

### Modular Design
- **Separation of Concerns**: Each module has a single responsibility
- **Clean Imports**: Easy to import and use specific components
- **Extensible**: Add new agents or services without modifying existing code
- **Maintainable**: Clear structure makes debugging and updates easier

### Advanced Routing Strategies
- **Sequential**: Execute agents in dependency order
- **Parallel**: Run independent agents simultaneously
- **Conditional**: Route based on business logic and conditions
- **Semantic**: Route based on user intent similarity
- **Priority**: Route based on agent priorities and load
- **Feedback**: Route based on historical performance

### Specialized Agents
- **Research Agent**: Gathers destination information, weather, accommodations
- **Planning Agent**: Creates detailed itineraries and schedules
- **Optimization Agent**: Optimizes costs and experiences
- **Booking Agent**: Handles reservations and payments
- **Monitoring Agent**: Provides real-time updates and adjustments

## 📦 Usage

### Basic Usage
```python
from src import TripPlannerOrchestrator, TripPreferences, RoutingStrategy
from datetime import datetime, timedelta

# Initialize orchestrator
orchestrator = TripPlannerOrchestrator("your_gemini_api_key")

# Create trip preferences
preferences = TripPreferences(
    budget=50000.0,
    duration_days=5,
    interests=['heritage', 'culture'],
    location='Rajasthan, India',
    start_date=datetime.now() + timedelta(days=30),
    travelers=2
)

# Plan trip with specific routing strategy
itinerary = await orchestrator.plan_trip(
    preferences, 
    RoutingStrategy.SEQUENTIAL
)
```

### Using Individual Components
```python
from src.config import TripPreferences, RoutingStrategy
from src.routing import AdvancedRouter
from src.agents.research_agent import ResearchAgent
from src.services import MultilingualSupport, PaymentIntegration

# Use individual agents
research_agent = ResearchAgent(llm)
results = await research_agent.arun(context)

# Use services
multilingual = MultilingualSupport(llm)
translated = await multilingual.translate_itinerary(itinerary, "hindi")
```

## 🔧 Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your Gemini API key:
```python
GEMINI_API_KEY = "your_gemini_api_key_here"
```

3. Run the demo:
```bash
python -m src.main
```

## 🏛️ Architecture Benefits

### Before (Monolithic)
- ❌ Single 674-line file
- ❌ All classes mixed together
- ❌ Hard to maintain and extend
- ❌ Difficult to test individual components
- ❌ Poor separation of concerns

### After (Modular)
- ✅ Clean separation into logical modules
- ✅ Each file has a single responsibility
- ✅ Easy to import specific components
- ✅ Simple to add new agents or services
- ✅ Better testability and maintainability
- ✅ Clear package structure with proper `__init__.py` files

## 🧪 Testing Different Routing Strategies

The system supports multiple routing strategies that can be easily tested:

```python
strategies = [
    RoutingStrategy.SEQUENTIAL,    # Step-by-step execution
    RoutingStrategy.PARALLEL,      # Simultaneous execution
    RoutingStrategy.CONDITIONAL,   # Rule-based routing
    RoutingStrategy.SEMANTIC,      # Intent-based routing
    RoutingStrategy.PRIORITY,      # Priority-based routing
    RoutingStrategy.FEEDBACK       # Performance-based routing
]

for strategy in strategies:
    itinerary = await orchestrator.plan_trip(preferences, strategy)
```

## 🔮 Extensibility

### Adding New Agents
1. Create a new agent file in `src/agents/`
2. Implement the `arun(context)` method
3. Add to the orchestrator's agent initialization
4. Update `src/agents/__init__.py`

### Adding New Services
1. Create a new service class in `src/services.py`
2. Add to the main package exports in `src/__init__.py`
3. Import and use as needed

### Adding New Routing Strategies
1. Add strategy to `RoutingStrategy` enum in `src/config.py`
2. Implement routing method in `src/routing.py`
3. Add to routing methods dictionary

## 📝 Dependencies

- `langchain`: Core AI agent framework
- `langchain-google-genai`: Google Gemini integration
- `google-generativeai`: Google AI SDK
- `numpy`: Numerical computations
- `asyncio`: Asynchronous programming

## 🤝 Contributing

1. Follow the modular structure
2. Add proper imports and exports
3. Update `__init__.py` files when adding new components
4. Maintain separation of concerns
5. Add appropriate docstrings and type hints

## 📄 License

This project demonstrates advanced AI agent routing patterns and modular architecture design principles.
