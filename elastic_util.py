from elasticsearch import Elasticsearch
import GLOBALS
import json

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
        return {"must" : {
                    "match_all" : {}
                }}
    else:
        return {
            "must": {
                "multi_match": {
                    "fields": ["restaurant", "item_name", "serving"],
                    "query": f"{keyword}"
                }
            }
        }

def _keyOptionalRestaurant(keyword):
    if keyword is None:
        return {"must" : {
                    "match_all" : {}
                }}
    else:
        return {
            "must": {
                    "multi_match": {
                        "fields": ["name"],
                        "query": f"{keyword}"
                    }
                }
        }

def elasticMenuQuery(keyword, distance, lat, lon, orderby=None, order="asc") -> 'json string':
    listResults = list()

    elastic_client = Elasticsearch([GLOBALS.ELASTIC_IP], http_auth=('user1', 'user1'), port=9200, use_ssl=False)

    body = {
        "size": 30,
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
        body["query"]["bool"] = _keyOptionalMenu(keyword)

    if orderby is not None:
        body["sort"] = [_getSortArg(orderby, lat, lon, order)]

    response = elastic_client.search(
        index="menu_index", body=body
    )

    for doc in response['hits']['hits']:
        listResults.append((doc["_id"], doc["_source"]))

    #print(json.dumps(listResults))
    return json.dumps(listResults)

#elasticMenuQuery("taco", 10, 33.6, -117.8, "brand_id")
#elasticMenuQuery("acai", 3, 33.6, -117.8)


def elasticRestaurantQuery(keyword, distance, lat, lon, denseVector=[0,0,0,0,0,0,0,0,0,0,0], orderby=None, order="asc") -> 'json string':
    listResults = list()

    elastic_client = Elasticsearch([GLOBALS.ELASTIC_IP], http_auth=('user1', 'user1'), port=9200, use_ssl=False)

    body = {
        #"_source": ["_id", "name", "brand_id", "address", "phone", "website", "lat_lon", "densevector"],
        "query" : {
        "bool" : {
          "must" : {
                "match_all" : {}
            }
        }
      }
    }

    script = {
        "source": "cosineSimilarity(params.query_vector, doc['densevector']) + 1.0",
        "params": {
            "query_vector": denseVector
        }
    }

    query = None
    if denseVector != [0,0,0,0,0,0,0,0,0,0,0]:
        inner = {"script_score": body}
        query = {"query": inner}
        query["query"]["script_score"]["script"] = script

    if keyword is not None:
        body["query"]["bool"] = _keyOptionalRestaurant(keyword)

    if orderby is not None:
        body["sort"] = [_getSortArg(orderby, lat, lon, order)]

    if denseVector != [0,0,0,0,0,0,0,0,0,0,0]:
        response = elastic_client.search(
            index="restaurant_index",
            body=query
        )
    else:
        response = elastic_client.search(
            index="restaurant_index",
            body=body
        )

    # BOMBS, [script=script] DOES NOT WORK
    # response = elastic_client.search(
    #     index="restaurant_index",
    #     body=body,
    #     script=script
    # )

    for doc in response['hits']['hits']:
        listResults.append(doc["_source"])

    #print(json.dumps(listResults))
    return json.dumps(listResults)


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

#elasticRestaurantQuery("taco", 5, 33.6, -117.8) # first hit: Taco Bell, "lat_lon": [{"lat": 33.72465515136719, "lon": -117.919921875}]
#elasticRestaurantQuery("taco", 5, 33.6, -117.8, vector) # first hit: Del Taco, 3329 South Harbor Boulevard
#elasticRestaurantQuery("taco", 5, 33.6, -117.8, vector, "_score") # sort by cosine similarity, different than above without sort


def elasticBrandIDQuery(brand_id, lat, lon, orderby=None, order="asc") -> 'json string':
    listResults = list()

    elastic_client = Elasticsearch([GLOBALS.ELASTIC_IP], http_auth=('user1', 'user1'), port=9200, use_ssl=False)

    body = {
        "size": 30,
        "query": {
            "bool": {
                "must": {
                    "term": {"brand_id": brand_id}
                }
            }
        }
    }

    if orderby is not None:
        body["sort"] = [_getSortArg(orderby, lat, lon, order)]

    response = elastic_client.search(index="restaurant_index", body=body)

    for doc in response['hits']['hits']:
        listResults.append(doc["_source"])

    return json.dumps(listResults)

#print(elasticBrandIDQuery("513fbc1283aa2dc80c000020", 33.6, -117.8))
