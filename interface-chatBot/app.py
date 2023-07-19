from flask import Flask, render_template, request, jsonify, session

"""
import sys
from pathlib import Path
# Add the parent directory to the Python module search path
sys.path.append(str(Path(__file__).resolve().parent.parent / 'chatbot-backend'))
"""
from in_context_learning_msg_api import get_response

app = Flask(__name__)
app.secret_key = 'secret_key'


@app.get('/') 
def index_get():
    return render_template('index.html')


@app.post('/chat')
def predict():
    if 'chat_turns' not in session:
        session['chat_turns'] = 0
    text = request.get_json().get('message')
    turns = session['chat_turns']
    #get response from model
    response = get_response(text, turns)
    message = {'answer': response}
    session['chat_turns'] += 1
    return jsonify(message)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)