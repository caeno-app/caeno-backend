import json
import requests

def getRestaurantsFromAPI(miles, lat, lng, limit=20):
    url = f"{base_url}{endpoints['location']}?ll={lat}%2C{lng}&distance={miles}mi&limit={limit}"

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return json.loads(response.content.decode('utf-8'))
    else:
        return None

if __name__ == "__main__":
    DEBUG = True

    #This should be moved I think.
    headers = {'x-app-id': '817c0683', 'x-app-key' : 'e6dd72bb3fed034be634d2eb5ea3977b', 'x-remote-user-id' : '0'}
    api_url = "https://trackapi.nutritionix.com/v2/locations?ll=33.6459%2C-117.8370&distance=50mi&limit=3"
    base_url = "https://trackapi.nutritionix.com/"
    endpoints = {"location" : "v2/locations"}

    if DEBUG:
        print(json.dumps(getRestaurantsFromAPI(5,33.64,-117.83,3),indent=2))

