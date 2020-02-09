from elasticsearch import Elasticsearch
import GLOBALS
import json

def getSortArg(orderby, lat, lon, order="asc"):
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


def elasticMenuQuery(keyword, distance, lat, lon, orderby=None, order="asc") -> 'json string':
    listResults = list()

    elastic_client = Elasticsearch([GLOBALS.ELASTIC_IP], http_auth=('user1', 'user1'), port=9200, use_ssl=False)

    body = {
        "_source": ["item_name", "brand_id", "calories", "restaurant", "serving"],
        # omit lat_long which could have 20+ entries
        "query": {
            "bool": {
                "must": {
                    "multi_match": {
                        "fields": ["restaurant", "item_name", "serving"],
                        "query": f"{keyword}"
                    }
                },
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
    if orderby is not None:
        body["sort"] = [getSortArg(orderby, lat, lon, order)]

    response = elastic_client.search(
        index="menu_index", body=body
    )

    for doc in response['hits']['hits']:
        listResults.append(doc["_source"])

    print(json.dumps(listResults))
    return json.dumps(listResults)

#elasticMenuQuery("taco", 10, 33.6, -117.8, "brand_id")
# elasticMenuQuery("acai", 3, 33.6, -117.8)


# returns nearby food items with just location in mind
def elMenuGENERAL(distance, lat, lon, orderby=None, order="asc") -> 'json string':
    listResults = list()

    elastic_client = Elasticsearch([GLOBALS.ELASTIC_IP], http_auth=('user1', 'user1'), port=9200, use_ssl=False)

    body = {
        "_source": ["item_name", "brand_id", "calories", "restaurant", "serving"],
        # omit lat_long which could have 20+ entries
        "query": {
            "bool" : {
                "must" : {
                    "match_all" : {}
                },
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
    if orderby is not None:
        body["sort"] = [getSortArg(orderby, lat, lon, order)]

    response = elastic_client.search(
        index="menu_index", body=body
    )

    for doc in response['hits']['hits']:
        listResults.append(doc["_source"])

    print(json.dumps(listResults))
    return json.dumps(listResults)

# elMenuGENERAL("acai", 3, 33.6, -117.8)


# returns nearby restaurants with just location in mind
def elRestaurantGENERAL(distance, lat, lon, orderby=None, order="asc") -> 'json string':
    listResults = list()

    elastic_client = Elasticsearch([GLOBALS.ELASTIC_IP], http_auth=('user1', 'user1'), port=9200, use_ssl=False)

    body = {
        "query": {
            "bool" : {
                "must" : {
                    "match_all" : {}
                },
                "filter" : {
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

    if orderby is not None:
        body["sort"] = [getSortArg(orderby, lat, lon, order)]

    response = elastic_client.search(
        index="restaurant_index",
        body=body
    )
    for doc in response['hits']['hits']:
        listResults.append(doc["_source"])
    return json.dumps(listResults)

# elRestaurantGENERAL(5, 33.6, -117.8)


def elasticRestaurantQuery(keyword, distance, lat, lon, orderby=None, order="asc") -> 'json string':
    listResults = list()

    elastic_client = Elasticsearch([GLOBALS.ELASTIC_IP], http_auth=('user1', 'user1'), port=9200, use_ssl=False)

    body = {
        "query": {
            "bool": {
                "must": {
                    "multi_match": {
                        "fields": ["name"],
                        "query": f"{keyword}"
                    }
                },
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

    if orderby is not None:
        body["sort"] = [getSortArg(orderby, lat, lon, order)]

    response = elastic_client.search(
        index="restaurant_index",
        body=body
    )
    for doc in response['hits']['hits']:
        listResults.append(doc["_source"])
    return json.dumps(listResults)


# elasticRestaurantQuery("taco", 5, 33.6, -117.8)


def elasticBrandIDQuery(brand_id, lat, lon, orderby=None, order="asc") -> 'json string':
    listResults = list()

    elastic_client = Elasticsearch([GLOBALS.ELASTIC_IP], http_auth=('user1', 'user1'), port=9200, use_ssl=False)

    body = {
        "query": {
            "bool": {
                "must": {
                    "term": {"brand_id": brand_id}
                }
            }
        }
    }

    if orderby is not None:
        body["sort"] = [getSortArg(orderby, lat, lon, order)]

    response = elastic_client.search(index="restaurant_index", body=body)

    for doc in response['hits']['hits']:
        listResults.append(doc["_source"])

    return json.dumps(listResults)

# print(elasticBrandIDQuery("513fbc1283aa2dc80c000020", 33.6, -117.8))
