from django.core.management.base import BaseCommand
import requests
from app.models import FoodBank  # Replace with your app's name
from app.models import FoodSource


class Command(BaseCommand):
        url = "https://api.geoapify.com/v2/places?categories=catering.restaurant,commercial.food_and_drink,catering.fast_food,catering.food_court&filter=rect:-131.79757822774695,43.46362686555679,-116.41427752962585,32.73770429604316&limit=200&apiKey=YOUR_API_KEY"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            for result in data.get('features', []):
                name = result.get('properties', {}).get('name', '')
                category = result.get('properties', {}).get('category', '')
                address = result.get('properties', {}).get('address', '')
                latitude = result.get('geometry', {}).get('coordinates', [])[1]
                longitude = result.get('geometry', {}).get('coordinates', [])[0]
                
                # Save each entry to the database
                FoodSource.objects.create(
                    name=name,
                    category=category,
                    address=address,
                    latitude=latitude,
                    longitude=longitude,
                    api_response=result  # Storing the entire API response as JSON if needed
                )
            
            self.stdout.write(self.style.SUCCESS('Successfully fetched and saved Geoapify data.'))
        else:
            self.stdout.write(self.style.ERROR('Failed to fetch data from Geoapify API.'))
