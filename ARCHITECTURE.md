# Architecture Overview

## Modular Structure Diagram

```
AI Trip Planner System
├── src/
│   ├── __init__.py              # Package exports
│   ├── config.py                # Data models & enums
│   ├── routing.py               # Advanced routing engine
│   ├── services.py              # Advanced services
│   ├── main.py                  # Demo & execution
│   └── agents/
│       ├── __init__.py          # Agent exports
│       ├── research_agent.py    # Information gathering
│       ├── planning_agent.py    # Itinerary creation
│       ├── optimization_agent.py # Cost optimization
│       ├── booking_agent.py     # Reservations
│       ├── monitoring_agent.py  # Real-time updates
│       └── orchestrator.py      # Main coordinator
```

## Component Relationships

```
TripPlannerOrchestrator
    ├── AdvancedRouter
    ├── ResearchAgent
    ├── PlanningAgent
    ├── OptimizationAgent
    ├── BookingAgent
    └── MonitoringAgent

Services Layer:
    ├── MultilingualSupport
    ├── RealTimeUpdates
    └── PaymentIntegration
```

## Data Flow

1. **Input**: TripPreferences → Orchestrator
2. **Routing**: Strategy selection → Agent execution
3. **Processing**: Agent results → Itinerary creation
4. **Output**: TripItinerary → User
5. **Adaptation**: Changes → Replanning
