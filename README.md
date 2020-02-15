# caeno-backend

### Get Nearby Restaurants:
--------------------------
**ROUTE: /api/elrestaurants**

http://172.112.215.241/api/elrestaurants?keyword=taco&dist=10&lat=33.645&lng=-117.843

Arguments:
| Name | Required | Description |
| --- | --- | --- |
| keyword | (optional) | keyword part of the restaurant's name |
| dist | required | maximum radius of search results (in miles) |
| lat | required | latitude (float) |
| lng | required | longitude (float) |


### Get Nearby Food Items
-------------------------
**ROUTE: /api/elmenu**

http://172.112.215.241/api/elmenu?dist=10&lat=33.645&lng=-117.843

Arguments:
| Name | Required | Description |
| --- | --- | --- |
| keyword | (optional) | keyword part of the item's name, or restaurant's name |
| dist | required | maximum radius of search results (in miles) |
| lat | required | latitude (float) |
| lng | required | longitude (float) |


### Nutrix API Get Nearby Restaurants
---------------------------------
**ROUTE: /api/nutrixrestaurants**

Arguments:
| Name | Required | Description |
| --- | --- | --- |
| dist | required | maximum radius of search results (in miles) |
| lat | required | latitude (float) |
| lng | required | longitude (float) |
| lim | (optional) | How many results to return (default = 20, max = 50) |

Usage example:
/restaurants?dist=2&lat=33.992&lng=-117.374&lim=2

```json
{
  "locations": [
    {
      "name": "Starbucks",
      "brand_id": "513fbc1283aa2dc80c00001f",
      "fs_id": null,
      "address": "3311 MARKET ST",
      "address2": null,
      "city": "Riverside",
      "state": "CA",
      "country": "US",
      "zip": "92501",
      "phone": "+19517829836",
      "website": "http://www.starbucks.com",
      "guide": null
      "id": 766916,
      "lat": 33.987220764160156,
      "lng": -117.37255096435547,
      "created_at": "2017-06-26T21:50:52.000Z",
      "updated_at": "2017-08-20T14:16:11.000Z",
      "distance_km": 0.5479654217321449
    },
    {
      "name": "Baker's Drive-thru",
      "brand_id": "513fbc1283aa2dc80c0001fc",
      "fs_id": null,
      "address": "2221 MAIN ST",
      "address2": null,
      "city": "Riverside",
      "state": "CA",
      "country": "US",
      "zip": "92501",
      "phone": "+19513289016",
      "website": "",
      "guide": null,
      "id": 2004912,
      "lat": 33.995418548583984,
      "lng": -117.36546325683594,
      "created_at": "2017-07-14T18:38:17.000Z",
      "updated_at": "2017-08-20T14:16:01.000Z",
      "distance_km": 0.8740053493738467
    }
  ]
}
```

### Run Program
-----------------------
```
# wget https://github.com/caeno-app/caeno-backend/archive/master.zip
# unzip master.zip
# cd caeno-backend-master/

# sudo apt-get install python3-pip -y
# pip3 install gunicorn
# pip3 install -r requirements.txt

# whereis gunicorn
# from output of whereis, use the path in first part of command below
# /home/user1/.local/bin/gunicorn --workers=3 app:app

#stops all gunicorn workers
pkill gunicorn
```
