# Research Agent for AI Trip Planner
import requests
from typing import Dict, Any, List

class ResearchAgent:
    """Agent specialized in gathering real-world travel information using OpenStreetMap APIs."""
    
    def __init__(self, llm):
        self.llm = llm
        self.nominatim_url = "https://nominatim.openstreetmap.org/search"
        self.overpass_url = "http://overpass-api.de/api/interpreter"

    def _get_location_coordinates(self, location_name: str) -> Dict[str, float]:
        """Converts a location name to latitude and longitude using Nominatim."""
        params = {'q': location_name, 'format': 'json', 'limit': 1}
        headers = {'User-Agent': 'AI-Trip-Planner/1.0'}
        try:
            response = requests.get(self.nominatim_url, params=params, headers=headers)
            response.raise_for_status()  # Raise an exception for bad status codes
            data = response.json()
            if data:
                return {
                    "lat": float(data[0]["lat"]),
                    "lon": float(data[0]["lon"])
                }
        except requests.exceptions.RequestException as e:
            print(f" Error fetching coordinates for {location_name}: {e}")
        return None

    def _find_points_of_interest(self, lat: float, lon: float, interests: List[str], radius: int = 10000) -> List[Dict[str, Any]]:
        """Finds points of interest (POIs) around a coordinate using Overpass API based on interests."""
        # A simple mapping from interests to Overpass API tags
        interest_tag_map = {
            'beaches': '"natural"="beach"',
            'nightlife': '"amenity"="nightclub"',
            'local food': '"amenity"="restaurant"',
            'culture': '"tourism"="museum"',
            'heritage': '"historic"="castle"',
            'adventure': '"leisure"="adventure_park"'
        }

        query_parts = []
        for interest in interests:
            if interest in interest_tag_map:
                query_parts.append(f"nwr[{interest_tag_map[interest]}](around:{radius},{lat},{lon});")

        if not query_parts:
            return []

        overpass_query = f"""[out:json];(
            {''.join(query_parts)}
        );
        out center;"""
        
        try:
            response = requests.post(self.overpass_url, data=overpass_query)
            response.raise_for_status()
            data = response.json()
            
            pois = []
            for element in data.get('elements', []):
                if 'tags' in element and 'name' in element['tags']:
                    pois.append({
                        'name': element['tags']['name'],
                        'type': element['tags'].get('amenity') or element['tags'].get('tourism') or 'attraction',
                        'lat': element.get('lat') or element.get('center', {}).get('lat'),
                        'lon': element.get('lon') or element.get('center', {}).get('lon')
                    })
            return pois
        except requests.exceptions.RequestException as e:
            print(f" Error querying Overpass API: {e}")
        return []

    async def arun(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute research tasks to find real-world places."""
        preferences = context.get('preferences')
        if not preferences:
            return {"error": "No preferences provided"}
        
        print(f" Researching location: {preferences.location}...")
        coordinates = self._get_location_coordinates(preferences.location)
        
        if not coordinates:
            return {"error": f"Could not find coordinates for {preferences.location}"}
        
        print(f" Found coordinates: {coordinates}")
        
        points_of_interest = self._find_points_of_interest(
            lat=coordinates['lat'],
            lon=coordinates['lon'],
            interests=preferences.interests
        )
        
        print(f" Found {len(points_of_interest)} points of interest.")
        
        return {
            "points_of_interest": points_of_interest[:20]  # Limit to 20 to keep it manageable
        }