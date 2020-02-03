from elasticsearch import Elasticsearch
import GLOBALS
import json

def elasticMenuQuery(keyword, distance, lat, lon) -> 'json string':
    listResults = list()

    elastic_client = Elasticsearch([GLOBALS.ELASTIC_IP], http_auth=('user1', 'user1'), port=9200, use_ssl=False)

    response = elastic_client.search(
        index="menu_index",
        body={
            "_source": ["item_name", "brand_id", "calories", "restaurant"],     # omit lat_long which could have 20+ entries
            "query": {
                "bool" : {
                    "must" : {
                        "multi_match" : {
                            "fields" : ["restaurant", "item_name"],
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