# Optimization Agent for AI Trip Planner
import json
from typing import Dict, Any, List
from ..config import ItineraryItem

class OptimizationAgent:
    """Agent specialized in optimizing itineraries for cost and experience using LLM reasoning."""
    
    def __init__(self, llm):
        self.llm = llm
        
    async def arun(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the itinerary and suggest cost-saving optimizations."""
        planning_results = context.get('previous_results', {}).get('planning', {})
        itinerary_items = planning_results.get('itinerary')
        total_cost = planning_results.get('total_cost', 0)
        preferences = context.get('preferences')
        
        if not itinerary_items or not preferences:
            return {"error": "No planning data or preferences provided to optimize"}

        print("💰 Optimization agent is looking for savings...")

        prompt = self._create_optimization_prompt(itinerary_items, total_cost, preferences.budget)

        response = await self.llm.ainvoke(prompt)
        llm_output = response.content.strip().replace('`json', '').replace('`', '')

        try:
            optimization_data = json.loads(llm_output)
            print(f"✅ Optimization agent finished. Found potential savings of ₹{optimization_data.get('estimated_savings', 0):,.2f}.")
            return {
                "cost_savings": optimization_data.get('estimated_savings', 0.0),
                "suggestions": optimization_data.get('suggestions', [])
            }
        except (json.JSONDecodeError, TypeError) as e:
            print(f"❌ Error parsing optimization from LLM: {e}")
            print(f"LLM Output was: {llm_output}")
            return {"error": "Failed to parse optimization plan from the LLM."}

    def _create_optimization_prompt(self, itinerary: List[ItineraryItem], current_cost: float, budget: float) -> str:
        """Creates a prompt for the LLM to optimize an itinerary."""
        
        itinerary_text = "\n".join([
            f"- Day {item.day} at {item.time}: {item.activity}, Cost: {item.cost:.2f} INR"
            for item in itinerary
        ])

        prompt = f"""
You are a frugal travel expert. Your task is to analyze a given travel itinerary and suggest specific, actionable ways to save money without significantly reducing the quality of the experience.

**Trip Details:**
- **User's Total Budget:** {budget:,.2f} INR
- **Current Estimated Itinerary Cost:** {current_cost:,.2f} INR

**Current Itinerary:**
{itinerary_text}

**Instructions:**
1.  Review the itinerary and identify activities or items that seem expensive.
2.  Provide 2-3 concrete suggestions for cost savings. For example, suggest a cheaper but equally good alternative for a restaurant, recommend using public transport, or find a free alternative to a paid attraction.
3.  For each suggestion, briefly explain the benefit.
4.  Estimate the total potential savings in INR from all your suggestions combined.
5.  Structure your output as a single JSON object with two keys:
    - `suggestions` (a list of strings): Each string should be a detailed suggestion.
    - `estimated_savings` (float): The total estimated amount of money saved in INR.

**Example Output:**
{{
    "suggestions": [
        "Instead of the guided tour at the City Palace, consider an audio guide which is much cheaper and offers flexibility.",
        "For lunch on Day 2, try the local street food market near the main square instead of a sit-down restaurant to save money and experience authentic local cuisine."
    ],
    "estimated_savings": 1500.0
}}

Now, generate the complete JSON output for your optimization suggestions.
"""
        return prompt
