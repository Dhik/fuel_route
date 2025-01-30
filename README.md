# Fuel Route Optimizer API

An intelligent API that helps truck drivers optimize their routes by finding the most cost-effective fuel stops between two locations in the USA.

## Features

- 🚛 Route optimization with fuel cost consideration 
- ⛽ Database of 6,700+ fuel stations with real-time prices
- 📍 Automatic geocoding of station locations
- 💰 Cost-effective stop suggestions
- 🔄 Considers vehicle range and fuel consumption

## Technical Specifications

- Vehicle Range: 500 miles
- Fuel Consumption: 10 MPG
- Framework: Django 3.2.23
- Database: SQLite (easily scalable to PostgreSQL)
- Routing Service: OpenStreetMap OSRM

## Installation

1. Clone the repository:
```bash
git clone https://github.com/dhik/fuel_route.git
cd fuel_route
```
2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```
3. Install dependencies:
```bash
pip install -r requirements.txt
```
4. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```
5. Load fuel station data:
```bash
python manage.py load_fuel_prices
```
# API Usage
## Optimize Route
## Endpoint: `POST /api/optimize`
## Request Body:
```bash
{
    "start_location": "Fort Smith, AR",
    "end_location": "Columbia, NJ"
}
```
## Response:
```bash
{
    "summary": {
        "start_location": "Fort Smith, AR",
        "end_location": "Columbia, NJ",
        "total_distance_miles": 1329.72,
        "total_cost_usd": 374.98,
        "number_of_stops": 3
    },
    "fuel_stops": [
        {
            "name": "STATION NAME",
            "address": "STATION ADDRESS",
            "city": "CITY",
            "state": "STATE", 
            "price": 2.82,
            "coordinates": {
                "lat": 32.163210,
                "lon": -94.369663
            }
        }
    ],
    "route_summary": {
        "bounds": {
            "northeast": {"lat": 41.20424, "lng": -75.09407},
            "southwest": {"lat": 35.38422, "lng": -94.43307}
        }
    }
}
```

## License
This project is licensed under the MIT License - see the LICENSE.md file for details
