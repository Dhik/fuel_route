import pandas as pd
from django.core.management.base import BaseCommand
from route_optimizer.models import FuelStation
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import time
import json
import os
import requests.exceptions

class Command(BaseCommand):
    help = 'Load fuel prices from CSV file'
    
    def __init__(self):
        super().__init__()
        self.checkpoint_file = 'import_checkpoint.json'
        self.geocoder = Nominatim(
            user_agent="fuel_station_loader",
            timeout=10
        )

    def load_checkpoint(self):
        if os.path.exists(self.checkpoint_file):
            with open(self.checkpoint_file, 'r') as f:
                return json.load(f)
        return {'last_processed_id': None, 'processed_count': 0}

    def save_checkpoint(self, last_id, count):
        if last_id is not None:
            with open(self.checkpoint_file, 'w') as f:
                json.dump({
                    'last_processed_id': int(last_id),
                    'processed_count': count
                }, f)

    def geocode_address(self, address, city, state, max_retries=3):
        for attempt in range(max_retries):
            try:
                address = ' '.join(address.split())
                full_address = f"{address}, {city}, {state}, USA"
                
                location = self.geocoder.geocode(full_address)
                if location:
                    return location.latitude, location.longitude
                
                time.sleep(2 ** attempt) 
            except (GeocoderTimedOut, GeocoderServiceError, requests.exceptions.RequestException) as e:
                if attempt == max_retries - 1:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Geocoding failed after {max_retries} attempts: {str(e)}"
                        )
                    )
                time.sleep(2 ** attempt)
        return None, None

    def handle(self, *args, **kwargs):
        try:
            self.stdout.write('Starting to load fuel prices...')
            
            checkpoint = self.load_checkpoint()
            last_processed_id = checkpoint['last_processed_id']
            count = checkpoint['processed_count']
            
            df = pd.read_csv('fuel-prices-for-be-assessment.csv')
            df = df.drop_duplicates(subset=['OPIS Truckstop ID'], keep='first')
            
            if last_processed_id is not None:
                df = df[df['OPIS Truckstop ID'] > last_processed_id]
                self.stdout.write(f'Resuming from ID {last_processed_id}, {count} stations already processed')
            else:
                FuelStation.objects.all().delete()
                count = 0
            
            total = len(df) + (count if last_processed_id is not None else 0)
            
            for _, row in df.iterrows():
                current_id = row['OPIS Truckstop ID']
                try:
                    if FuelStation.objects.filter(truckstop_id=current_id).exists():
                        continue
                        
                    lat, lon = self.geocode_address(
                        row['Address'],
                        row['City'],
                        row['State']
                    )
                    
                    station = FuelStation(
                        truckstop_id=current_id,
                        name=row['Truckstop Name'],
                        address=row['Address'],
                        city=row['City'],
                        state=row['State'],
                        rack_id=row['Rack ID'],
                        price=row['Retail Price'],
                        latitude=lat,
                        longitude=lon
                    )
                    
                    station.save()
                    count += 1
                    
                    if count % 10 == 0:
                        self.save_checkpoint(current_id, count)
                        self.stdout.write(f'Processed {count}/{total} stations')
                        
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Error processing station {row['Truckstop Name']}: {str(e)}"
                        )
                    )
                    self.save_checkpoint(current_id, count)
                    continue
            
            if os.path.exists(self.checkpoint_file):
                os.remove(self.checkpoint_file)
                
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully loaded {count} fuel stations'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f"Failed to load fuel prices: {str(e)}"
                )
            )
            if 'current_id' in locals():
                self.save_checkpoint(current_id, count)