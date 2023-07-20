import re
from flask import Flask, render_template, request, jsonify, session, redirect
from flask_session import Session
from 
from backend_utilities import get_response,search_doctors, send_email, DoctorCategoryAssistant
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key!'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# render the index.html page
@app.route("/", methods=["GET", "POST"]) 
def index():
    return render_template('index.html')

# store the user name, age, email, address... info  in session
# session act as global variable here
@app.route("/form", methods=["POST", "GET"])
def form():
    if request.method == "POST":
        # record the user name
        session["name"] = request.form.get("name")
        #session["age"] = request.form.get("age")
        #....
        # store all the info in database
        #storeInfo()

        # redirect to the main page
        return redirect("/")
    return render_template("form.html")

# chatbot interface for online chat
@app.post('/chatOnline')
def chat():
    text = request.get_json().get('message')
    #get response from model
    response = get_response(text)
    # jsonify the response
    message = {'answer': response}
    return jsonify(message)

# chatbot interface for using SMS
@app.post('/chatSMS')
def chatSMS():
    incoming_msg = request.values['Body']
    # use phone number as session_id
    session_id = request.values['From']
    r = MessagingResponse()
    """
    msg = get_response(incoming_msg)
    r.message(msg)
    """
    # below is for testing
    r.message('this is the response')
    return str(r)

#def storeInfo():
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)