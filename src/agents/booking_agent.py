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