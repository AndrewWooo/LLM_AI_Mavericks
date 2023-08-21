from flask import Flask, render_template, request, jsonify, session, redirect
from flask_session import Session
from backend_utilities import get_response, addSystemMessage, send_email, getDoctor
import os

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
    session.pop('categoryRecom', None) # clear the categoryRecom in session
    session.pop('scheduledTime', None) # clear the scheduledTime in session
    #session.pop('formFilled', None) # clear the formFilled in session
    return render_template('form.html')

# store the user name, age, email, address... info  in session
# session act as global variable here
@app.route("/chat", methods=["POST", "GET"])
def form():
    if request.method == "POST":# record the user info in session
        session['formFilled'] = True
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
        #return redirect("/chatOnline")
    return render_template("index.html")

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
                return jsonify({'answer': "Please enter your avaible time:", 'calendar':"openCalendar"}), 200
            elif text.lower() == 'n' or text.lower() == 'no':
                session['consentOfAppt'] = 'n'
                return jsonify({'answer': "Goodbye!"}), 200
            else: # cases that user input is not y or n
                return jsonify({'answer': "If you want to make a Appt., enter y to continue"}), 200
        elif session.get('consentOfAppt') == 'y': # input is the available time, may be we need widget later
            if session.get('categoryRecom') is None:
                session['scheduledTime'] = text
                ctgy = session.get('category') # predicted category
                path= os.path.dirname(os.path.abspath(__name__))
                # Searching for the doctors
                dr_recom = getDoctor(ctgy, path)
                session['categoryRecom'] = dr_recom['doctors']
                return jsonify({'answer': dr_recom['reply'],'doctorList':dr_recom['doctors']})
            else:
                receiver_email = session.get('email')
                choosedCate = session.get('categoryRecom')
                reason = session.get('cateReasoning')
                time = session.get('scheduledTime')
                for doctor1 in choosedCate:
                    if doctor1['Name'][0] == text:
                        dr_address = doctor1['Address'][0]
                        break
                dr_name = text
                if dr_name =='error':
                    return jsonify({'answer': "Ops, some errors happens!"}), 200
                # send email to the patient
                subject = f'Confirmed with your appointment with {dr_name} <br>Address:{dr_address} <br>Time: {time}'
                subject1 = f'Confirmed with your appointment with {dr_name};  Address:{dr_address};  Time: {time}' 
                mailbody = f"""{reason} \n\n  Here is the doctor we recommend: \n     Doctor Name: {dr_name}\n     Address: {dr_address} \n     We checked the doctor is avaiable at time: {time}
                    """
                successSend=send_email(receiver_email, subject1, mailbody)
                if successSend=='success':
                    return jsonify({'answer': subject,'additionalInfo':"A reminder email will be sent to you later. You are all set, goodbye!"}), 200
                else:
                    return jsonify({'answer': "Ops, some errors happens with send email"}), 200
        else:  #session.get('consentOfAppt') == 'n'
            session.pop('consentOfAppt', None) # clear the category in session
            return jsonify({'answer': "Ops, some errors happens!If you want to make a Appt., enter y to continue"}), 200


    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)