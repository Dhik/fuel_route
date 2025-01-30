from rest_framework import serializers
from .models import FuelStation

class RouteInputSerializer(serializers.Serializer):
    start_location = serializers.CharField(max_length=255)
    end_location = serializers.CharField(max_length=255)

class FuelStationSerializer(serializers.ModelSerializer):
    class Meta:
        model = FuelStation
        fields = '__all__'

class RouteResponseSerializer(serializers.Serializer):
    route_polyline = serializers.CharField()
    fuel_stops = FuelStationSerializer(many=True)
    total_cost = serializers.DecimalField(max_digits=8, decimal_places=2)
    total_distance = serializers.FloatField()