from rest_framework import views
from rest_framework.response import Response
from rest_framework import status
from .serializers import RouteInputSerializer, RouteResponseSerializer
from .utils.optimization import FuelOptimizer

class OptimalRouteView(views.APIView):
    def post(self, request):
        serializer = RouteInputSerializer(data=request.data)
        if serializer.is_valid():
            optimizer = FuelOptimizer(
                serializer.validated_data['start_location'],
                serializer.validated_data['end_location']
            )
            
            result = optimizer.find_optimal_stops()
            
            if result:
                response_data = {
                    'summary': {
                        'start_location': serializer.validated_data['start_location'],
                        'end_location': serializer.validated_data['end_location'],
                        'total_distance_miles': round(result['total_distance'], 2),
                        'total_cost_usd': round(result['total_cost'], 2),
                        'number_of_stops': len(result['stops'])
                    },
                    'fuel_stops': [{
                        'name': stop.name,
                        'address': stop.address,
                        'city': stop.city,
                        'state': stop.state,
                        'price': float(stop.price),
                        'coordinates': {
                            'lat': stop.latitude,
                            'lon': stop.longitude
                        }
                    } for stop in result['stops']],
                    'route_summary': {
                        'bounds': {
                            'northeast': result.get('bounds', {}).get('northeast', {}),
                            'southwest': result.get('bounds', {}).get('southwest', {})
                        },
                        'path_coordinates': result.get('path_coordinates', [])[:100]
                    }
                }
                return Response(response_data)
            return Response(
                {"error": "Could not calculate route"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
