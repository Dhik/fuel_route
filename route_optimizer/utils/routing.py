import requests
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

class RouteCalculator:
    def __init__(self):
        self.geocoder = Nominatim(user_agent="fuel_route_optimizer")
        self.osrm_url = "http://router.project-osrm.org/route/v1/driving/"

    def geocode_location(self, location):
        try:
            location_data = self.geocoder.geocode(location + ", USA")
            if location_data:
                return (location_data.latitude, location_data.longitude)
            return None
        except Exception as e:
            print(f"Geocoding error: {e}")
            return None

    def get_route(self, start_coords, end_coords):
        url = f"{self.osrm_url}{start_coords[1]},{start_coords[0]};{end_coords[1]},{end_coords[0]}"
        params = {
            "overview": "full",
            "geometries": "polyline",
            "steps": "true"
        }
        
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                route_data = response.json()
                if 'routes' in route_data and len(route_data['routes']) > 0:
                    route = route_data['routes'][0]
                    return {
                        'distance': route.get('distance', 0) / 1000,
                        'duration': route.get('duration', 0),
                        'geometry': route.get('geometry', '')
                    }
            return None
        except Exception as e:
            print(f"Routing error: {e}")
            return None