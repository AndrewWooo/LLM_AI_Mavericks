import requests
import json

url = 'http://localhost:5010/appointment'
data = {
    'patient_input': 'I have a headache.',
    'predicted_category': 'Neurologist',
    'patient_address': '123 Main St, Anytown, USA',
    'receiver_email': 'john.doe@example.com',
    'patient_free_time': 'Tomorrow at 2pm',
    'assistant_reply': 'I recommend you to see a neurologist.'
}

response = requests.post(url, data=json.dumps(data))
print(response.json())
