
from flask import Flask, request, Response
import logging
import api_util as api
import json

DEBUG = True

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello"

@app.route('/restaurants/<int:restaurant_id>')
def get_restaurant_data(restaurant_id):
    return "Information about:" + str(restaurant_id)

@app.route('/restaurants')
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

    
# @app.errorhandler(500)
# def internal_error(error):
#     return render_template('errors/500.html'), 500


# @app.errorhandler(404)
# def not_found_error(error):
#     return render_template('errors/404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)