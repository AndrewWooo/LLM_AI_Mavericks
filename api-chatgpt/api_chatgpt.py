from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

@app.route('/api', methods=['POST'])
def api():
    # Parse the JSON body
    content = request.get_json()

    if 'content' not in content:
        return jsonify({'error': 'Missing content'}), 400

    # Read the API key from api-key.txt
    with open('api-key.txt', 'r') as file:
        apiKey = file.read().replace('\n', '')

    # Call OpenAI API
    url = 'https://api.openai.com/v1/chat/completions'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {apiKey}'
    }
    data = {
        'model': 'gpt-3.5-turbo',
        'messages': [{'role': 'user', 'content': content['content']}],
        'temperature': 0.7
    }

    res = requests.post(url, headers=headers, data=json.dumps(data))
    response = res.json()

    # Format and send the response
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(port=8080)
