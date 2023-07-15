from flask import Flask, render_template, request, jsonify

import sys
from pathlib import Path
# Add the parent directory to the Python module search path
sys.path.append(str(Path(__file__).resolve().parent.parent / 'LLM_Dev'))



app = Flask(__name__)



@app.get('/') 
def index_get():
    return render_template('index.html')


@app.post('/chat')
def predict():
    text = request.get_json().get('message')
    
    #get response from model
    response = "get_response(text)"
    message = {'answer': response}
    
    return jsonify(message)

if __name__ == '__main__':
    app.run(debug=True)