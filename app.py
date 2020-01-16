
from flask import Flask, request
import logging

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello"

@app.route('/restaurants/<int:restaurant_id>')
def get_restaurant_data(restaurant_id):
    return "Information about:" + str(restaurant_id)

@app.route('/restaurants')
def get_restaurant_data_all():
    lat = request.args.get('lat')
    lng = request.args.get('lng')
    return ("Lattitude: " + lat + "\nLongitude: " + lng)

# @app.errorhandler(500)
# def internal_error(error):
#     return render_template('errors/500.html'), 500


# @app.errorhandler(404)
# def not_found_error(error):
#     return render_template('errors/404.html'), 404

if __name__ == '__main__':
    app.run()