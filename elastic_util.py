from elasticsearch import Elasticsearch
import GLOBALS
import json

def elasticMenuQuery(keyword, distance, lat, lon) -> 'json string':
    listResults = list()

    elastic_client = Elasticsearch([GLOBALS.ELASTIC_IP], http_auth=('user1', 'user1'), port=9200, use_ssl=False)

    response = elastic_client.search(
        index="menu_index",
        body={
            "_source": ["item_name", "brand_id", "calories", "restaurant", "serving"],     # omit lat_long which could have 20+ entries
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
                "bool" : {
                    "must" : {
                        "multi_match" : {
                            "fields" : ["restaurant", "item_name", "serving"],
                            "query" : f"{keyword}"
                        }
                    },
                    "filter" : {
                        "geo_distance" : {
                            "distance" : f"{distance}mi",
                            "lat_lon" : {
                                "lat" : lat,
                                "lon" : lon
                            }
                        }
                    }
                }
            }
        }
    )

    for doc in response['hits']['hits']:
        listResults.append(doc["_source"])

    return json.dumps(listResults)

#elasticMenuQuery("acai", 3, 33.6, -117.8)


def elasticRestaurantQuery(keyword, distance, lat, lon) -> 'json string':
    listResults = list()

    elastic_client = Elasticsearch([GLOBALS.ELASTIC_IP], http_auth=('user1', 'user1'), port=9200, use_ssl=False)

    response = elastic_client.search(
        index="restaurant_index",
        body={
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
                "bool" : {
                    "must" : {
                        "multi_match" : {
                            "fields" : ["name"],
                            "query" : f"{keyword}"
                        }
                    },
                    "filter" : {
                        "geo_distance" : {
                            "distance" : f"{distance}mi",
                            "lat_lon" : {
                                "lat" : lat,
                                "lon" : lon
                            }
                        }
                    }
                }
            }
        }
    )

    for doc in response['hits']['hits']:
        listResults.append(doc["_source"])

    return json.dumps(listResults)

#elasticRestaurantQuery("taco", 5, 33.6, -117.8)


def elasticBrandIDQuery(brand_id, lat, lon) -> 'json string':
    listResults = list()

    elastic_client = Elasticsearch([GLOBALS.ELASTIC_IP], http_auth=('user1', 'user1'), port=9200, use_ssl=False)

    response = elastic_client.search(
        index="restaurant_index",
        body={
            "sort":[
                {
                    "_geo_distance" : {
                        "lat_lon" : [lon, lat],
                        "order" : "asc",
                        "unit" : "mi",
                        "mode" : "min",
                        "distance_type" : "arc"
                    }
                }
            ],
            "query": {
                "bool" : {
                    "must" : {
                        "term" : { "brand_id" : brand_id }
                      }
                }
            }
        }
    )

    for doc in response['hits']['hits']:
        listResults.append(doc["_source"])

    return json.dumps(listResults)


#print(elasticBrandIDQuery("513fbc1283aa2dc80c000020", 33.6, -117.8))