# Import the required library
from flask import Flask, jsonify, request
from serpapi import GoogleSearch
import requests
from geopy.geocoders import Nominatim

app = Flask(__name__)

# Read the API key from api-key.txt
with open('api-key_googleMap.txt', 'r') as file:
    api_key = file.read().strip()
    

@app.route('/search', methods=['GET'])
def search_doctors():
    doctorType = request.args.get('doctorType')
    address = request.args.get('address')

    if not doctorType or not address:
        return jsonify({'error': 'Missing required parameters.'}), 400
    
    # Initialize Nominatim API
    geolocator = Nominatim(user_agent="MyApp")

    # address = "14449 south quiet shade dr, herriman, ut 84096"

    location = geolocator.geocode(address)
    

    if location:
        latitude = location.latitude
        longitude = location.longitude

        params = {
            "api_key": api_key,
            "engine": "google_maps",
            "type": "search",
            "google_domain": "google.com",
            "q": doctorType,
            "hl": "en",
            "ll": f"@{latitude},{longitude},14z"
        }

        search = GoogleSearch(params)
        results = search.get_dict()

        doctors = []
        for result in results['local_results']:
            name = result['title']
            address = result['address']
            doctors.append({'name': name, 'address': address})

        return jsonify({doctorType: doctors})
    else:
        return jsonify({'error': 'Geocoding failed. Invalid address or API error.'}), 400

if __name__ == '__main__':
    app.run()
