import requests

url = 'http://localhost:5010/get_patient_info/john.doe@example.com'

response = requests.get(url)
print(response.json())
