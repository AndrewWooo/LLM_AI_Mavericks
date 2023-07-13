import requests
from pprint import pprint
import time

# Set the API endpoint URL
# url = 'http://169.254.97.204:5000/search'
url = 'http://googmap-service:5000/search'

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
    # Pretty-print the data
    pprint(data)
    # Process the data returned by the API
    # ...
else:
    # Error response
    print(f"API error: {response.status_code} - {response.json()['error']}")

# Sleep for one hour
time.sleep(60*60)

# Exit
exit(0)