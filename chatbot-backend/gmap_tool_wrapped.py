import os
from langchain.agents import tool
# from flask import Flask, jsonify, request
from serpapi import GoogleSearch
# import requests
from geopy.geocoders import Nominatim
serpapi_key = os.environ.get('SERPAPI_KEY')

@tool
def search_doctors(doctorType: str, address: str):
    """Returns are the doctor's name and address, both are strings. \
    use this when the agent want to help user to make an appointment with a doctor and \
    after the user provide the one's address, \
    The inputs are two variables, first one is doctorType: str, \
    second one is address: str.\
    it also return errors if Missing required parameters \
    or Geocoding failed. Invalid address or API error"""
    top_k = 1
    if not doctorType or not address:
    	return 'error', 'Missing required parameters.'
        # return jsonify({'error': 'Missing required parameters.'}), 400
    # Initialize Nominatim API
    geolocator = Nominatim(user_agent="MyApp")
    # address = "14449 south quiet shade dr, herriman, ut 84096"
    location = geolocator.geocode(address)
    if location:
        latitude = location.latitude
        longitude = location.longitude
        params = {
            "api_key": serpapi_key,
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
        for result in results['local_results'][:top_k]:
            name = result['title']
            address = result['address']
            doctors.append({'name': name, 'address': address})
        return doctors[0]['name'], doctors[0]['address']
    else:
        return 'error', 'Geocoding failed. Invalid address or API error.'


ans = search_doctors('General Practitioner', "2204 New College Ln, Plano, TX 75025")


