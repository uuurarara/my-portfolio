#緯度・経度を取得するロジックの実装
import requests

def get_lat_lng(station_name):
    api_key = 'YOUR_GOOGLE_MAPS_API_KEY'
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={station_name}&key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['results']:
            location = data['results'][0]['geometry']['location']
            return location['lat'], location['lng']
    return None, None


def calculate_midpoint(lat1, lng1, lat2, lng2):
    if None in (lat1, lng1, lat2, lng2):
        raise ValueError("One or more coordinates are not set. Please ensure all users have valid latitude and longitude.")
    
    midpoint_lat = (lat1 + lat2) / 2
    midpoint_lng = (lng1 + lng2) / 2
    return midpoint_lat, midpoint_lng

