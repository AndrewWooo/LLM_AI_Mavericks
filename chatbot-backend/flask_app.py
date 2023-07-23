from flask import Flask, render_template, request, jsonify
from backend_utilities import *
import openai
import os
import sqlite3

app = Flask(__name__)

openai.api_key = os.getenv('OPENAI_API_KEY')
sender_email = os.environ.get('SENDER_EMAIL')
sender_password = os.environ.get('SENDER_PIN')
database_file = 'patients.db'

# Global variables to store user responses and step
user_responses = []
step = 0

# Conversation flow
conversation = [
    ("AI", "Hello!"),
    ("User", ""),  # Placeholder for the user's greeting
    ("AI", "What's your email address?"),
    ("User", ""),  # Placeholder for the user's email input
    ("AI", "Thank you for providing your email address. Do you want to make an appointment (y/n)?"),
    ("User", ""),  # Placeholder for the user's response to making an appointment
    ("AI", "Sure, I will help you on it."),
    ("AI", "Goodbye.")
]

@app.route('/')
def home():
    # Start the conversation with the bot's greeting
    user_responses.append(('AI', conversation[step][1]))
    return render_template('home.html', messages=user_responses)

@app.route('/process', methods=['POST'])
def process():
    global step, user_responses
    user_input = request.form['user_input']
    user_responses.append(('User', user_input))

    # Increment the step right after getting user input
    step += 1

    # Check user input for email and appointment response
    if step == 3:  # User has entered email
        if "@" not in user_input:
            step -= 1
            return jsonify("Sorry, I didn't understand your email address. Please provide a valid email.")
    elif step == 5:  # User has answered appointment question
        if user_input.lower() not in ['y', 'n']:
            step -= 1
            return jsonify("Please type 'y' or 'n'.")
        elif user_input.lower() == 'y':
            return jsonify(conversation[6][1])  # Agent helps with the appointment
        else:  # 'n'
            return jsonify(conversation[7][1])  # Agent says goodbye

    # Send the agent's next message if we are not at the end of the conversation
    if step < len(conversation):
        return jsonify(conversation[step][1])
    else:
        return jsonify("End of Conversation")

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    patient_input = data.get('patient_input')
    assistant = DoctorCategoryAssistant()
    assistant.messages.append({
        "role": "user",
        "content": patient_input
    })

    # Generate a response from the model
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo-0613',
        messages=assistant.messages,
        max_tokens=128,
        n=1,
        stop=None,
        temperature=0.6,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )

    # Extract the assistant's reply
    assistant_reply = response.choices[0].message['content']

    return jsonify({"assistant_reply": assistant_reply}), 200

@app.route('/create_patient', methods=['POST'])
def create_patient():
    data = request.get_json()

    # Data validation: you'd want to ensure that all required fields are present
    required_fields = ['last_name', 'first_name', 'email', 'gender', 'age', 'medical_records']

    if not all(field in data for field in required_fields):
        return jsonify({"message": "Missing required fields"}), 400

    # Data processing: extract each field from the JSON data
    last_name = data['last_name']
    first_name = data['first_name']
    email = data['email']
    gender = data['gender']
    age = data['age']
    medical_records = data['medical_records']

    try:
        conn = sqlite3.connect(database_file)
        cursor = conn.cursor()

        # Insert data into database
        cursor.execute('''
            INSERT INTO patients (last_name, first_name, email, gender, age, medical_records)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (last_name, first_name, email, gender, age, json.dumps(medical_records)))

        conn.commit()

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return jsonify({"message": "Database error"}), 500
    except Exception as e:
        print(f"Exception in _query: {e}")
        return jsonify({"message": "An error occurred"}), 500

    return jsonify({"message": "Patient created successfully!"}), 201

@app.route('/get_patient_info/<email>', methods=['GET'])
def get_patient_info(email):
    conn = sqlite3.connect(database_file)
    cursor = conn.cursor()

    # Retrieve the data from the database
    cursor.execute("SELECT * FROM patients WHERE email=?", (email,))
    result = cursor.fetchone()

    if result is None:
        return jsonify({"error": "No patient found with that email."}), 404

    # Assuming your table structure is (id, last_name, first_name, gender, age, email, medical_records)
    patient_info = {
        'id': result[0],
        'last_name': result[1],
        'first_name': result[2],
        'gender': result[3],
        'age': result[4],
        'email': result[5],
        'medical_records': eval(result[6])  # Be careful with eval, only use if you're sure the data is safe!
    }

    return jsonify(patient_info), 200

@app.route('/appointment', methods=['POST'])
def make_appointment():
    data = request.get_json()

    patient_input = data.get('patient_input')
    predicted_category = data.get('predicted_category')
    patient_address = data.get('patient_address')
    receiver_email = data.get('receiver_email')
    patient_free_time = data.get('patient_free_time')
    assistant_reply = data.get('assistant_reply')

    # If any of the required fields are missing in the request, return an error
    if None in [patient_input, predicted_category, patient_address, receiver_email, patient_free_time]:
        return jsonify({"error": "Missing required field(s)."}), 400

    # Searching for the doctors
    doctor_recom = search_doctors(predicted_category, patient_address)
    dr_name = doctor_recom[0]
    err = 0
    while dr_name == 'error':
        if err > 2:
            return jsonify({"error": "System issue encountered, please try again later."}), 500
        # In case of invalid address, you may want to handle this in a different way
        # because we can't ask for input in an API. This is just for illustrative purposes.
        err += 1
    dr_address = doctor_recom[1]

    # Confirmation message
    subject = "Doctor Appoint confirmation"
    message = f"""{assistant_reply} \n
                The clinic/doctor's name is {dr_name}, whose address is {dr_address} \n
                at time: {patient_free_time}
                """
    send_email(sender_email, sender_password, receiver_email, subject, message)

    return jsonify({"message": "Appointment confirmed!"}), 200


if __name__ == "__main__":
    app.run(port=5010)
