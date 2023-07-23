import requests
import json

url = 'http://localhost:5010/create_patient'
data = {
    'last_name': 'Doe',
    'first_name': 'John',
    'email': 'john.doe@example.com',
    'gender': 'Male',
    'age': 30,
    'medical_records': {
        'allergies': ['Peanuts'],
        'medications': ['Ibuprofen']
    }
}

response = requests.post(url, data=json.dumps(data))
print(response.json())
