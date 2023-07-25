from flask import Flask, render_template, request, jsonify, session, redirect, g
from flask_session import Session
from backend_utilities import get_response, addSystemMessage, send_email, search_doctors
from twilio.twiml.messaging_response import MessagingResponse


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key!'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# render the index.html page
@app.route("/", methods=["GET", "POST"]) 
def index():
    # Each time refreshing the webpage:
    session.pop('category', None) # clear the category in session
    session.pop('consentOfAppt', None) # clear the consentOfAppt in session
    return render_template('index.html')

# store the user name, age, email, address... info  in session
# session act as global variable here
@app.route("/form", methods=["POST", "GET"])
def form():
    if request.method == "POST":# record the user info in session
        session['formFilled'] = True
        session.pop('category', None) # clear the category in session
        session.pop('consentOfAppt', None) # clear the consentOfAppt in session
        session['phone'] = request.form.get("phone")
        session['email'] = request.form.get("email")
        session['address'] = request.form.get("address")
        gender=session['gender']= request.form.get("gender") #
        age= session['age'] = request.form.get("age") #
        smoke= session['smoke'] = request.form.get("smoke") #
        medR=session['medical_records'] = request.form.get("medical_records") #
        session['height'] = request.form.get("height") 
        session['weight'] = request.form.get("weight")
        
        # add the user info to the assistant object
        addSystemMessage(gender, age, smoke, medR)
        
        # store all the info in database
        #storeInfo()
        # redirect to the main page
        return redirect("/")
    return render_template("form.html")

# chatbot interface for online chat
@app.post('/chatOnline')
def chat():
    text = request.get_json().get('message')
    # let customer fill out the form first
    if session.get('formFilled') != True :
        return jsonify({'answer': "Ops. Please click start and fill out the form first!"})
    # if the category is not in session, then the user is gonna ask question, call get_response()
    if session.get('category') is None: 
        #get response from model
        response = get_response(text)
        if response.get('category') is not None and response.get('followMsg') is not None:
            session['cateReasoning'] = response['reply']
            session['category'] = response['category']
            message = {'answer': response['reply'], 'additionalInfo': response['followMsg']}
            return jsonify(message)
        else:
        # jsonify the response
            message = {'answer': response['reply']}
            return jsonify(message)
    else: # if the category is already in session, then the user is gonna make appointment
        if session.get('consentOfAppt') is None:
            if text.lower() == 'y' or text.lower() == 'yes':
                session['consentOfAppt'] = 'y'
                # let user input avaiable time
                return jsonify({'answer': "Please enter your avaible time"}), 200
            elif text.lower() == 'n' or text.lower() == 'no':
                session['consentOfAppt'] = 'n'
                return jsonify({'answer': "Goodbye!"}), 200
            else: # cases that user input is not y or n
                return jsonify({'answer': "If you want to make a Appt., enter y to continue"}), 200
        elif session.get('consentOfAppt') == 'y': # input is the available time, may be we need widget later
            ctgy = session.get('category') # predicted category
            addrs = session.get('address') # address
            receiver_email = session.get('email')
            reason = session.get('cateReasoning')
            # Searching for the doctors
            dr_recom = search_doctors(ctgy, addrs)
            dr_name = dr_recom[0]
            dr_address = dr_recom[1]
            if dr_name =='error':
                return jsonify({'answer': "Ops, some errors happens!"}), 200
            # send email to the patient
            subject = f'Your appointment with {dr_name} at {dr_address} \nat time: {text}' 
            mailbody = f"""{reason} \n
                Here is the doctor we recommend: {dr_name}, whose address is {dr_address} \n
                We checked the doctor is avaiable at time: {text}
                """
            send_email(receiver_email, subject, mailbody)
            return jsonify({'answer': subject,'additionalInfo':"A reminder email will be sent to you later."}), 200
        else:  #session.get('consentOfAppt') == 'n'
            session.pop('consentOfAppt', None) # clear the category in session
            return jsonify({'answer': "Ops, some errors happens!If you want to make a Appt., enter y to continue"}), 200


    


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


    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)