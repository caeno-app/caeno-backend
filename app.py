from flask import Flask, request, Response
from flask_cors import CORS, cross_origin

import api_util as api
import json
import elastic_util

DEBUG = True

app = Flask(__name__)

# https://stackoverflow.com/questions/38641785/specify-domains-for-flask-cors
CORS(app, resources={r"/api/*": {"origins": "*"}})
# CORS(app, resources={r"/api/*": {"origins": ["caeno.app",domain2.com]}})

# https://flask-cors.corydolphin.com/en/latest/api.html#decorator
# more specific modifiers that can be added to routes above ^

@app.route('/')
def home():
    return "Hello"

# # can individually specify allowed domains able to call route using @cross_origin
# @cross_origin(["domain1.com", "domain2.com"])
@app.route('/api/restaurants/<int:restaurant_id>')
def get_restaurant_data(restaurant_id):
    return "Information about:" + str(restaurant_id)

# runs query against Nutrix API, not elasticsearch
@app.route('/api/nutrixrestaurants', methods=['GET'])
def get_restaurant_locations():
    try:
        dist = int(request.args.get('dist'))
        lng = float(request.args.get('lng'))
        lat = float(request.args.get('lat'))
        lim = request.args.get('lim')

        if lim is None:
            lim = 20
        else:
            lim = float(lim)

        response = api.getRestaurantsFromAPI(dist,lat,lng,lim)
        return Response(response=json.dumps(response.json()),status=response.status_code,mimetype="application/json")

    except ValueError:
        return Response(response= "{'error': 'Failed to parse request.' }",status=400,mimetype="application/json")


@app.route('/api/elrestaurants', methods=['GET'])
def get_nearby_restaurants():
    try:
        keyword = request.args.get('keyword')
        dist = int(request.args.get('dist'))
        lng = float(request.args.get('lng'))
        lat = float(request.args.get('lat'))

        # if not keyword:
        #     return "no keyword used"

        json_response = elastic_util.elasticRestaurantQuery(keyword, dist, lat, lng)
        return Response(response=json_response, status=200, mimetype="application/json")

    except ValueError:
        return Response(response= "{'error': 'Failed to parse request.' }",status=400,mimetype="application/json")

# http://127.0.0.1:5000/api/elrestaurants?keyword=taco&dist=10&lat=33.645&lng=-117.843


@app.route('/api/elmenu', methods=['GET'])
def get_nearby_food():
    try:
        keyword = request.args.get('keyword')
        dist = int(request.args.get('dist'))
        lng = float(request.args.get('lng'))
        lat = float(request.args.get('lat'))

        # if not keyword:
        #     return "no keyword used"

        json_response = elastic_util.elasticMenuQuery(keyword, dist, lat, lng)
        return Response(response=json_response, status=200, mimetype="application/json")

    except ValueError:
        return Response(response= "{'error': 'Failed to parse request.' }",status=400,mimetype="application/json")

# http://127.0.0.1:5000/api/elmenu?keyword=taco&dist=10&lat=33.645&lng=-117.843

# @app.errorhandler(500)
# def internal_error(error):
#     return render_template('errors/500.html'), 500


# @app.errorhandler(404)
# def not_found_error(error):
#     return render_template('errors/404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)