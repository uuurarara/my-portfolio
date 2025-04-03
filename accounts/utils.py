#緯度・経度を取得するロジックの実装
import requests

def get_lat_lng(station_name):
    api_key = 'AIzaSyDj92_8szXIvPxCIlLaxSBzhH1k4MW30Dg'
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={station_name}&key={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # HTTPエラーを検出
        data = response.json()
        if data['status'] == 'OK' and data['results']:
            location = data['results'][0]['geometry']['location']
            return location['lat'], location['lng']
        else:
            print(f"Geocode失敗: {data.get('status')}")
    except requests.exceptions.RequestException as e:
        print(f"APIエラー: {e}")
    return None, None

def calculate_midpoint(lat1, lng1, lat2, lng2):
    if None in (lat1, lng1, lat2, lng2):
        raise ValueError("One or more coordinates are not set. Please ensure all users have valid latitude and longitude.")
    
    midpoint_lat = (lat1 + lat2) / 2
    midpoint_lng = (lng1 + lng2) / 2
    return midpoint_lat, midpoint_lng

