from .routing import RouteCalculator
from ..models import FuelStation
from django.db.models import Q
from geopy.distance import geodesic

class FuelOptimizer:
    def __init__(self, start_location, end_location):
        self.route_calculator = RouteCalculator()
        self.start_location = start_location
        self.end_location = end_location
        self.max_range = 500 
        self.mpg = 10 
        
    def find_optimal_stops(self):
        try:
            start_coords = self.route_calculator.geocode_location(self.start_location)
            end_coords = self.route_calculator.geocode_location(self.end_location)
            
            if not (start_coords and end_coords):
                return None
                
            route_info = self.route_calculator.get_route(start_coords, end_coords)
            if not route_info:
                return None
                
            total_distance = route_info['distance'] * 0.621371
            
            optimal_stops = self._find_stations_along_route(
                start_coords, 
                end_coords, 
                route_info,
                max(0, int(total_distance / self.max_range))
            )
            
            path_coordinates = self._decode_polyline(route_info.get('geometry', ''))
            
            if not path_coordinates: 
                path_coordinates = [
                    [start_coords[0], start_coords[1]],
                    [end_coords[0], end_coords[1]]
                ]
            
            lats = [coord[0] for coord in path_coordinates]
            lngs = [coord[1] for coord in path_coordinates]
            
            bounds = {
                'northeast': {
                    'lat': max(lats),
                    'lng': max(lngs)
                },
                'southwest': {
                    'lat': min(lats),
                    'lng': min(lngs)
                }
            }
            
            return {
                'stops': optimal_stops,
                'total_distance': total_distance,
                'total_cost': self._calculate_total_cost(optimal_stops, total_distance),
                'bounds': bounds,
                'path_coordinates': [{'lat': coord[0], 'lng': coord[1]} 
                                for coord in path_coordinates[:100]]
            }
            
        except Exception as e:
            print(f"Error in find_optimal_stops: {str(e)}")
            if start_coords and end_coords:
                return {
                    'stops': optimal_stops if 'optimal_stops' in locals() else [],
                    'total_distance': total_distance if 'total_distance' in locals() else 0,
                    'total_cost': self._calculate_total_cost(
                        optimal_stops if 'optimal_stops' in locals() else [], 
                        total_distance if 'total_distance' in locals() else 0
                    ),
                    'bounds': {
                        'northeast': {'lat': max(start_coords[0], end_coords[0]),
                                    'lng': max(start_coords[1], end_coords[1])},
                        'southwest': {'lat': min(start_coords[0], end_coords[0]),
                                    'lng': min(start_coords[1], end_coords[1])}
                    },
                    'path_coordinates': [
                        {'lat': start_coords[0], 'lng': start_coords[1]},
                        {'lat': end_coords[0], 'lng': end_coords[1]}
                    ]
                }
            return None

    
    def _find_stations_along_route(self, start_coords, end_coords, route_info, min_stops):
        stations = []
        current_position = start_coords
        
        while len(stations) < min_stops + 1:
            nearby_stations = FuelStation.objects.filter(
                latitude__isnull=False,
                longitude__isnull=False
            ).order_by('price')[:10] 
            
            best_station = None
            best_score = float('inf')
            
            for station in nearby_stations:
                distance = geodesic(
                    current_position, 
                    (station.latitude, station.longitude)
                ).miles
                
                if distance <= self.max_range:
                    price_float = float(station.price)
                    score = price_float * distance
                    if score < best_score:
                        best_score = score
                        best_station = station
            
            if best_station:
                stations.append(best_station)
                current_position = (best_station.latitude, best_station.longitude)
            else:
                break
                
        return stations
    
    def _calculate_total_cost(self, stops, total_distance):
        total_gallons = total_distance / self.mpg
        total_cost = 0.0
        
        if stops:
            gallons_per_stop = total_gallons / len(stops)
            for station in stops:
                total_cost += float(station.price) * gallons_per_stop
        
        return total_cost

    def _decode_polyline(self, polyline):
        """Decodes a polyline string into a list of coordinates"""
        coordinates = []
        index = 0
        lat = 0
        lng = 0
        
        while index < len(polyline):
            shift = 0
            result = 0
            while True:
                byte = ord(polyline[index]) - 63
                index += 1
                result |= (byte & 0x1F) << shift
                shift += 5
                if not byte >= 0x20:
                    break
            lat_change = ~(result >> 1) if (result & 1) else (result >> 1)
            lat += lat_change

            shift = 0
            result = 0
            while True:
                byte = ord(polyline[index]) - 63
                index += 1
                result |= (byte & 0x1F) << shift
                shift += 5
                if not byte >= 0x20:
                    break
            lng_change = ~(result >> 1) if (result & 1) else (result >> 1)
            lng += lng_change

            coordinates.append([lat / 100000.0, lng / 100000.0])

        return coordinates