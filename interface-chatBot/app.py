from flask import Flask, render_template, request, jsonify, session
from in_context_learning_msg_api import get_response

app = Flask(__name__)
#app.secret_key = 'my_secret_key'


@app.get('/') 
def index_get():
    return render_template('index.html')


@app.post('/chatOnline')
def predict():
    
    text = request.get_json().get('message')
    """
    chat_log = session.get('chat_log')
    if chat_log is None:
        chat_log = '''assistant: Hi, what brought you here today?'''
    #store the chat log
    session['chat_log'] = f'{chat_log}user: {text}\nassistant: {response}\n'
    """
    #get response from model
    response = get_response(text)
    # jsonify the response
    message = {'answer': response}
    return jsonify(message)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)