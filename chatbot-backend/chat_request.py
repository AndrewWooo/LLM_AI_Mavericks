import requests
import json

url = 'http://localhost:5010/chat'
data = {
    'patient_input': 'I have a headache.'
}

response = requests.post(url, data=json.dumps(data))
print(response.json())