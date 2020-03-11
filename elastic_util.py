from elasticsearch import Elasticsearch
import GLOBALS
import json
from scipy import spatial
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import random
import nltk

nltk.download('punkt')

FoodTypes = {0: "Drink", 1: "Dessert", 2: "Breakfast", 3: "Japanese", 4: "Mexican", 5: "Chinese", 6: "American",
             7: "Italian", 8: "Indian", 9: "Mediterranean", 10: "Other"}
stop_words = set(stopwords.words('english'))
DELIMITERS = ["(", "-", ":", ";", ","]
for d in DELIMITERS:
    stop_words.add(d)


def _getSortArg(orderby, lat, lon, order="asc"):
    # TODO: Check if orderby is a valid column in db
    # We have the option to not sort at all, or sort by a specific field,
    #  in either ascending or decending order.

    if orderby == "dist":
        return {"_geo_distance": {
            "lat_lon": [lon, lat],
            "order": "asc" if order == "asc" else "desc",
            "unit": "mi",
            "mode": "min",
            "distance_type": "arc"}}
    else:
        return {orderby: {
            "order": "asc" if order == "asc" else "desc",
            "mode": "min"}}


def _keyOptionalMenu(keyword):
    if keyword is None:
        return {
            "match_all": {}
        }
    else:
        return {
            "multi_match": {
                "fields": ["restaurant", "item_name", "serving"],
                "query": f"{keyword}"
            }
        }


def _keyOptionalRestaurant(keyword):
    if keyword is None:
        return {
            "match_all": {}
        }
    else:
        return {
            "multi_match": {
                "fields": ["name"],
                "query": f"{keyword}"
            }
        }


def _createItemGroups(items):
    groups = dict()
    for item in items:
        groupID = item["item_name"].lower()
        tokens = word_tokenize(groupID)
        for t in tokens:
            if t in stop_words:
                i = groupID.find(t) - 1
                while i > 0 and (groupID[i] in DELIMITERS or groupID[i] == " "):
                    i -= 1

                if i > 3:
                    groupID = groupID[:i + 1]
                    break

        if groupID not in groups:
            groups[groupID] = list()
        groups[groupID].append(item)

    return [{"group_id": k, "items": v} if (len(v) > 1) else v[0] for k, v in groups.items()]


def elasticRecomendedMenuItems(vector, distance, lat, lon, limit=1000):
    elastic_client = Elasticsearch([GLOBALS.ELASTIC_IP], http_auth=('user1', 'user1'), port=9200, use_ssl=False)
    body = {
        "size": limit,
        "_source": ["_id", "item_name", "brand_id", "calories", "restaurant", "serving"],
        "query": {
            "bool": {
                "filter": {
                    "geo_distance": {
                        "distance": f"{distance}mi",
                        "lat_lon": {
                            "lat": lat,
                            "lon": lon
                        }
                    }
                }
            }
        }
    }
    temp = list()
    if vector != [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]:
        for i, x in enumerate(vector):
            weight = round(float(x) * limit)
            if weight > 1:
                body["query"]["bool"]["must"] = {"match": {"food_type": FoodTypes[i]}}
                body["size"] = weight
                response = elastic_client.search(index="menu_index", body=body)

                for doc in response['hits']['hits']:
                    doc["_source"]["_id"] = doc["_id"]
                    temp.append(doc["_source"])
    else:
        response = elastic_client.search(index="menu_index", body=body)
        for doc in response['hits']['hits']:
            doc["_source"]["_id"] = doc["_id"]
            temp.append(doc["_source"])

    results = _createItemGroups(
        [x for x in temp if ("calories" in x and x["calories"] is not None and x["calories"] >= 120)])
    random.shuffle(results)

    brandLimit = 5
    limiter = dict()
    limitedResults = list()
    for x in results:
        bid = x["brand_id"] if "group_id" not in x else x["items"][0]["brand_id"]
        if bid not in limiter:
            limiter[bid] = 0
        if limiter[bid] <= brandLimit:
            limiter[bid] += 1
            limitedResults.append(x)

    return json.dumps(limitedResults, indent=1)

# vector = [0.04297994269340974,
#  0.034383954154727794,
#  0.20916905444126074,
#  0.04011461318051576,
#  0.04297994269340974,
#  0.0,
#  0.38108882521489973,
#  0.24068767908309455,
#  0.0,
#  0.0,
#  0.008595988538681949]

# http://127.0.0.1:5000/api/recommendeditems?vector=[0,0,0,0,0,0,0,0,0,0,0]&dist=10&lat=33.645&lng=-117.843


def elasticMenuQuery(keyword, distance, lat, lon, orderby=None, order="asc") -> 'json string':
    listResults = list()

    elastic_client = Elasticsearch([GLOBALS.ELASTIC_IP], http_auth=('user1', 'user1'), port=9200, use_ssl=False)

    body = {
        "size": 350,
        "_source": ["_id", "item_name", "brand_id", "calories", "restaurant", "serving"],
        # omit lat_long which could have 20+ entries
        "query": {
            "bool": {
                "filter": {
                    "geo_distance": {
                        "distance": f"{distance}mi",
                        "lat_lon": {
                            "lat": lat,
                            "lon": lon
                        }
                    }
                }
            }
        }
    }
    if keyword is not None:
        body["query"]["bool"]["must"] = _keyOptionalMenu(keyword)

    if orderby is not None:
        body["sort"] = [_getSortArg(orderby, lat, lon, order)]

    response = elastic_client.search(
        index="menu_index", body=body
    )

    for doc in response['hits']['hits']:
        doc["_source"]["_id"] = doc["_id"]
        listResults.append(doc["_source"])

    # print(json.dumps(listResults))
    return json.dumps(_createItemGroups(listResults), indent=1)


def elasticRestaurantQuery(distance, lat, lon, denseVector=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                           keyword=None, orderby=None, order="asc") -> 'json string':
    elastic_client = Elasticsearch([GLOBALS.ELASTIC_IP], http_auth=('user1', 'user1'), port=9200, use_ssl=False)

    body = {
        "size": 150,
        "sort": [
            {
                "_geo_distance": {
                    "lat_lon": [lon, lat],
                    "order": "asc",
                    "unit": "mi",
                    "mode": "min",
                    "distance_type": "arc"
                }
            }
        ],
        "query": {
            "bool": {
                # "must": {"match_all": {}
                #          },
                "filter": {
                    "geo_distance": {
                        "distance": f"{distance}mi",
                        "lat_lon": {
                            "lat": lat,
                            "lon": lon
                        }
                    }
                }
            }
        }
    }

    body["query"]["bool"]["must"] = _keyOptionalRestaurant(keyword)

    response = elastic_client.search(
        index="restaurant_index", body=body
    )

    # Remove duplicates and compute similarity to user vector
    included = set()
    withoutDuplicates = list()
    for doc in response['hits']['hits']:
        if doc["_source"]["brand_id"] not in included:
            included.add(doc["_source"]["brand_id"])
            doc["_source"]["_id"] = doc["_id"]

            if denseVector != [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]:
                doc["_source"]["similarity"] = (1 - spatial.distance.cosine(denseVector, doc["_source"]["densevector"]))
            else:
                doc["_source"]["similarity"] = -1

            withoutDuplicates.append(doc["_source"])

    # Sort by similarity if the user vector is not the zero vector.
    if denseVector == [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]:
        return json.dumps(withoutDuplicates)
    else:
        return json.dumps(sorted(withoutDuplicates, key=lambda v: v["similarity"], reverse=True), indent=1)


# vector = [0.04297994269340974,
#  0.034383954154727794,
#  0.20916905444126074,
#  0.04011461318051576,
#  0.04297994269340974,
#  0.0,
#  0.38108882521489973,
#  0.24068767908309455,
#  0.0,
#  0.0,
#  0.008595988538681949]

# http://127.0.0.1:5000/api/elrestaurants?keyword=taco&dist=10&lat=33.645&lng=-117.843&vector=[0,0,0,0,0,0,0,0,0,0,0]
# elasticRestaurantQuery("taco", 5, 33.6, -117.8) # first hit: Taco Bell, "lat_lon": [{"lat": 33.72465515136719, "lon": -117.919921875}]
# elasticRestaurantQuery("taco", 5, 33.6, -117.8, vector) # first hit: Del Taco, 3329 South Harbor Boulevard
# elasticRestaurantQuery("taco", 5, 33.6, -117.8, vector, "_score") # sort by cosine similarity, different than above without sort

def elasticBrandIDRestaurant(brand_id) -> 'json string':
    listResults = list()

    elastic_client = Elasticsearch([GLOBALS.ELASTIC_IP], http_auth=('user1', 'user1'), port=9200, use_ssl=False)

    body = {
        "size": 80,
        "_source": ["_id", "name", "brand_id", "address", "phone", "website", "lat_lon"],
        "query": {
            "bool": {
                "must": {
                    "term": {"brand_id": brand_id}
                }
            }
        }
    }

    response = elastic_client.search(index="restaurant_index", body=body)

    for doc in response['hits']['hits']:
        doc["_source"]["_id"] = doc["_id"]
        listResults.append(doc["_source"])

    return json.dumps(listResults)


def elasticAllMenuBrandID(brand_id) -> 'json string':
    listResults = list()
    elastic_client = Elasticsearch([GLOBALS.ELASTIC_IP], http_auth=('user1', 'user1'), port=9200, use_ssl=False)
    body = {
        "size": 5000,
        "_source": ["_id", "item_name", "calories"],
        "query": {
            "bool": {
                "must": {
                    "term": {"brand_id": brand_id}
                }
            }
        }
    }
    response = elastic_client.search(index="menu_index", body=body)

    for doc in response['hits']['hits']:
        doc["_source"]["_id"] = doc["_id"]
        listResults.append(doc["_source"])

    #print(_createItemGroups(listResults))
    return json.dumps(_createItemGroups(listResults), indent=1)


def elasticBrandIDVector(brand_id) -> 'json string':
    elastic_client = Elasticsearch([GLOBALS.ELASTIC_IP], http_auth=('user1', 'user1'), port=9200, use_ssl=False)

    body = {
        "size": 1,
        "_source": ["densevector"],
        "query": {
            "bool": {
                "must": {
                    "term": {"brand_id": brand_id}
                }
            }
        }
    }

    response = elastic_client.search(index="restaurant_index", body=body)

    for doc in response['hits']['hits']:
        return json.dumps(doc["_source"])

# print(elasticBrandIDVector("513fbc1283aa2dc80c0000b4"))