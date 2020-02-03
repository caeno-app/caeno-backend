import json
import requests
import GLOBALS

X_APP_KEY = GLOBALS.X_APP_KEY
X_APP_ID = GLOBALS.X_APP_ID

def getRestaurantsFromAPI(miles, lat, lng, limit=20):
    headers = {'x-remote-user-id' : '0', 'x-app-id': X_APP_ID, 'x-app-key' : X_APP_KEY}
    base_url = "https://trackapi.nutritionix.com/"
    endpoints = {"location" : "v2/locations"}
    url = f"{base_url}{endpoints['location']}?ll={lat}%2C{lng}&distance={miles}mi&limit={limit}"
    return requests.get(url, headers=headers)

