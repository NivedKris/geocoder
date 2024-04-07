# geocoder.py
import os
import requests

google_maps_api_key= os.getenv('GOOGLE_MAPS_API_KEY')

def geocode_address(address):
    url = f'https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={google_maps_api_key}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data.get('results'):
            # Assuming the first result is the most relevant
            first_result = data['results'][0]
            geometry = first_result.get('geometry')
            if geometry:
                location = geometry.get('location')
                if location:
                    latitude = location.get('lat')
                    longitude = location.get('lng')
                    return latitude, longitude
                

    return None, None
