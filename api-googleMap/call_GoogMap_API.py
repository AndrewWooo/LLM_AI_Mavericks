import requests

# Set the API endpoint URL
url = 'http://169.254.97.204:5000/search'  

# Set the parameters: doctorType and address
doctorTpye = "orthodontists"
address = '1600 Amphitheatre Parkway, Mountain View, CA'

params = {
    'doctorType': doctorTpye,
    'address': address
}

# Send the GET request to the API
response = requests.get(url, params=params)

# Check the response status code
if response.status_code == 200:
    # Successful response
    data = response.json()
    # Process the data returned by the API
    # ...
else:
    # Error response
    print(f"API error: {response.status_code} - {response.json()['error']}")
