# Advanced Routing Engine for AI Trip Planner
import asyncio
import numpy as np
from typing import Dict, List, Any
from collections import defaultdict

from .config import AgentType, RoutingStrategy


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
            # RoutingStrategy.CONDITIONAL: self._conditional_routing,
            # RoutingStrategy.SEMANTIC: self._semantic_routing,
            # RoutingStrategy.PRIORITY: self._priority_routing,
            # RoutingStrategy.FEEDBACK: self._feedback_routing
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
        # Extract and enhance context for better LLM understanding
        budget = context.get('budget', 0)
        duration = context.get('duration_days', 0)
        interests = context.get('interests', [])
        location = context.get('location', '').lower()
        
        # Define conditions with clear thresholds
        conditions = {
            'budget_high': budget > 100000,
            'duration_long': duration > 7,
            'complex_interests': len(interests) > 3,
            'international': location not in ['india', 'domestic']
        }
        
        # Add context for LLM to understand the routing decisions
        context['routing_context'] = {
            'conditions_checked': {
                'is_high_budget': (budget > 100000, f"Budget ₹{budget:,.2f} > ₹100,000"),
                'is_long_duration': (duration > 7, f"Duration {duration} days > 7 days"),
                'has_complex_interests': (len(interests) > 3, f"{len(interests)} interests > 3"),
                'is_international': (location not in ['india', 'domestic'], f"Location: {location}")
            },
            'active_rule': None  # Will be set below
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
                # Update context with the active rule for LLM transparency
                context['routing_context']['active_rule'] = {
                    'rule': active_rule,
                    'agents': [agent.value for agent in routing_rules[active_rule]],
                    'reason': f"Condition met: {condition.replace('_', ' ').title()}"
                }
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
