import json
import requests
import GLOBALS
import time
import multiprocessing
from collections import deque
from math import asin,cos,pi,sin,floor,ceil,sqrt
import numpy as np
import classifier

rEarth = 6371.01   # earth radius (km)
epsilon = 0.000001

X_APP_KEY = GLOBALS.X_APP_KEY
X_APP_ID = GLOBALS.X_APP_ID

def getRestaurantsFromAPI(miles, lat, lng, limit=20):
    headers = {'x-remote-user-id' : '0', 'x-app-id': X_APP_ID, 'x-app-key' : X_APP_KEY}
    base_url = "https://trackapi.nutritionix.com/"
    endpoints = {"location" : "v2/locations"}
    url = f"{base_url}{endpoints['location']}?ll={lat}%2C{lng}&distance={miles}mi&limit={limit}"
    results = requests.get(url, headers=headers)
    return results

def getMenuItems(brandID):
    base_url = "https://www.nutritionix.com/nixapi/brands/"
    url = f"{base_url}{brandID}/items/1?&limit=2000"
    results = requests.get(url)
    return results

def deg2rad(angle):
    return angle*pi/180

def rad2deg(angle):
    return angle*180/pi

def pointRadialDistance(lat1, lon1, bearing, distance):
    """
    Return final coordinates (lat2,lon2) [in degrees] given initial coordinates
    (lat1,lon1) [in degrees] and a bearing [in degrees] and distance [in km]
    """
    rlat1 = deg2rad(lat1)
    rlon1 = deg2rad(lon1)
    rbearing = deg2rad(bearing)
    rdistance = distance / rEarth # normalize linear distance to radian angle

    rlat = asin( sin(rlat1) * cos(rdistance) + cos(rlat1) * sin(rdistance) * cos(rbearing) )

    if cos(rlat) == 0 or abs(cos(rlat)) < epsilon: # Endpoint a pole
        rlon=rlon1
    else:
        rlon = ( (rlon1 - asin( sin(rbearing)* sin(rdistance) / cos(rlat) ) + pi ) % (2*pi) ) - pi

    lat = rad2deg(rlat)
    lon = rad2deg(rlon)
    return (lat, lon)

def getCoveringPoints(centerLat, centerLng, stepRad,targetRad):
    factor = 6.0
    currentRad = stepRad
    points = []
    points.append((centerLat,centerLng))
    while currentRad < targetRad:
        for i in range(ceil(factor)):
            points.append(pointRadialDistance(centerLat, centerLng,((360/factor) * i),currentRad))

        nextRad = sqrt( pow((currentRad + stepRad),2) * cos(2*pi / factor))
        ratio = nextRad/currentRad
        factor = factor * ratio
        currentRad = nextRad
        assert(currentRad >= 1)

    return points

def extendedRestaurantLocations(lat, lng, dist, res = 1):
    """
    Return set of restaurants within dist miles of (lat,lng)
    - lat: center latitude
    - lng: center longitude
    - dist: radius of search area (in miles)
    - res: min = 1, max = 5, use 1 for the most accuracy (it will take longer)
    """
    dist = min(dist, 50)
    if res > 5:
        res = 5
    elif res < 1:
        res = 1
    else:
        res = round(res)
    
    restaurants = {}

    points = getCoveringPoints(lat,lng,res,dist)
    for point in points:
        results = getRestaurantsFromAPI(res, point[0], point[1], 50).json()
        for rest in results["locations"]:
            restaurants[rest["id"]] = rest

    return restaurants

def getNewRestaurantData(lat, lng, rManager, classify, conn):
    #Relative to the given location, obtain a list of restaurants
    restaurants = extendedRestaurantLocations(lat,lng,5,5)

    newBrands = set()
    for rest in restaurants.values():
         if not rManager.hasRestaurant(rest["brand_id"]):
             newBrands.add((rest["brand_id"], rest["name"]))

    #Create new feature vectors for any new brands encountered.
    newBrandMenus = dict()
    for nb in newBrands:
        menu = getMenuItems(nb[0])
        if menu.status_code == 200:
            restaurant = classifier.Restaurant(nb[0],nb[1])
            newBrandMenus[nb[0]] = {"brand_info": dict(), "menu": list()}
            menu = menu.json()["items"]
            predictions = classify.predictList(menu)

            for i, item in enumerate(menu):
                restaurant.addItem(predictions[i])
                newBrandMenus[nb[0]]["menu"].append(item)
            
            restaurant.normalize()
            newBrandMenus[nb[0]]["brand_info"]["vector"] = restaurant.vector
            newBrandMenus[nb[0]]["brand_info"]["restaurant"] = restaurant.name

    conn.send([newBrandMenus, restaurants])
    conn.close()

class tManager(object):
    def __init__(self, limit):
        self._lock = multiprocessing.Lock()
        self.activeCount = 0
        self.maxProcesses = limit
        self.timeOut = 120       #2 minute processing limit
        self.taskQueue = deque()
        self.processes = dict()
        self.restaurantManager = classifier.RestaurantManager("r_features.json")
        self.classify = classifier.Classifier(itemsPath="classified.json", modelPath="model.sav")
    
    def addTask(self, lat, lng):
        self.taskQueue.append((lat,lng))

    def _spawnProcesses(self):
        #There is still work to be done and we have not spawned the maximum number of processes
        while self.activeCount < self.maxProcesses and len(self.taskQueue) > 0:
            lat, lng = self.taskQueue.popleft()
            parentCon, childCon = multiprocessing.Pipe()
            p = multiprocessing.Process(target=getNewRestaurantData, args=(lat,lng, self.restaurantManager, self.classify, childCon))
            self.processes[p] = (parentCon, time.time())
            p.start()
            self.activeCount += 1
           
    
    def _processResults(self, results):
        if len(results[0]) > 0:
            for brand, data in results[0].items():
                if not self.restaurantManager.hasRestaurant(brand):
                    self.restaurantManager.addRestaurant(brand,data["brand_info"]["restaurant"],data["brand_info"]["vector"])
                    #TODO: determine if it is safe to insert duplicates into elastic search. If duplicates are politely rejected, 
                    # processes should use elastic bulk api to insert their data instead of introducing this bottleneck here.
                    #print(brand,data["brand_info"]["restaurant"],data["brand_info"]["vector"])

    def _monitorProcesses(self):
        #Only join and retrieve data from processes that sent data through their designated pipe.
        clean = []
        for p in self.processes.keys():
            if self.processes[p][0].poll(.001):
                results = self.processes[p][0].recv()
                self.processes[p][0].close()
                p.join()
                self._processResults(results) #This is a really big potential bottleneck
                self.activeCount -= 1
                clean.append(p)
            elif self.processes[p][1] + self.timeOut < time.time():
                self.processes[p][0].close()
                p.terminate()
                self.activeCount -= 1
                clean.append(p)
        
        #Delete any handles to processes that were closed
        for p in clean:
            del self.processes[p]
        
    def tick(self):
        self._spawnProcesses()
        self._monitorProcesses()

    def hasTask(self):
        return (len(self.taskQueue) > 0)

    def processIsActive(self):
        return (self.activeCount > 0)

if __name__ == "__main__":
    manager = tManager(2) #max threads = 2
    coords = [(33.6459258,-117.8312514),(34.9481184,-120.4197442),(33.9481184,-120.427442)]
    for c in coords:
        manager.addTask(c[0], c[1])

    manager.tick()
    while manager.processIsActive() or manager.hasTask():
        manager.tick()
        time.sleep(5)

    



