# caeno-backend

Routes:
/restaurants

Arguments: 
- dist (in miles)
- lat
- lng
- lim (optional, default = 20, max = 50)

Usage example:
/restaurants?dist=2&lat=33.992&lng=-117.374&lim=2

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

