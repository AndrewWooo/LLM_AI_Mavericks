import os
import json
import openai
import sqlite3
import pickle
from fuzzywuzzy import fuzz
# api 
from flask import Flask, request, jsonify

from serpapi import GoogleSearch
# import requests
from geopy.geocoders import Nominatim

import smtplib
import ssl
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from backend_utilities import *
serpapi_key = os.environ.get('SERPAPI_KEY')

api_key = os.environ.get('OPENAI_API_KEY')
openai.api_key = api_key

sender_email = os.environ.get('SENDER_EMAIL')
sender_password = os.environ.get('SENDER_PIN')


app = Flask(__name__)

database_file = 'patients.db'

if os.path.exists(database_file):
    os.remove(database_file)


conn = sqlite3.connect(database_file)
cursor = conn.cursor()

# Create a table to store patient information
cursor.execute('''
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        last_name TEXT,
        first_name TEXT,
        gender TEXT, 
        age INTEGER,
        email TEXT,
        medical_records TEXT
    )
''')

file_dir = os.path.dirname(os.path.abspath(__name__))

# Load the dictionary back from the pickle file
with open(f'{file_dir}/patient_db.p', "rb") as f:
    patients_with_medical_records = pickle.load(f)


# Insert the sample data into the database
cursor.executemany('INSERT INTO patients (last_name, first_name, email, gender, age, medical_records) VALUES (?, ?, ?, ?, ?, ?)', patients_with_medical_records)


patient_form = {'receiver_email' :'ray.jianlei.zhang@gmail.com',
'patient_address' : "2204 New College Ln, Plano, TX 75025",
'first_name': "Jay", "last_name": "Zhang", 'smoke': 'No', 
'patient_free_time' : "today at 3:00pm CDT"
}



receiver_email = patient_form['receiver_email']
patient_address = patient_form['patient_address']

patient_free_time = patient_form['patient_free_time']


# Retrieve the data from the database
cursor.execute("SELECT * FROM patients WHERE email=?", (receiver_email,))
result = cursor.fetchone()


fields = ['last_name', 'first_name', 'email', 'gender', 'age', 'medical_records']
patient_info = {x:y for x, y in zip(fields, result[1:])}
patient_info['medical_records'] = eval(patient_info['medical_records'] )
patient_info



# Create an instance of the DoctorCategoryAssistant class
assistant = DoctorCategoryAssistant()


# Load patient information from a JSON file
# print('script_dir', script_dir)
# with open(f'{script_dir}/patient_1.json') as f:
#     patient_info = json.load(f)

# Extract patient details
# patient_description = patient_info['description']
smoke = patient_form['smoke']
age = patient_info['age']
gender = patient_info['gender']
medical_records = patient_info['medical_records']

# System message
assistant.messages.append({"role": "system", "content": assistant.logic})
# assistant.messages.append({"role": "system", "content": f"Patient Description: {patient_info['description']}"})
assistant.messages.append({"role": "system", "content": f"smoke or not: {smoke}"})
assistant.messages.append({"role": "system", "content": f"Patient Age: {patient_info['age']}"})
assistant.messages.append({"role": "system", "content": f"Patient Gender: {patient_info['gender']}"})
assistant.messages.append({"role": "system", "content": f"Patient Medical Records: {patient_info['medical_records']}"})

print("Assistant: Hello, what brought you here today?")
patient_input = input("Patient: ")

# Add the patient's input to the conversation
assistant.messages.append({
    "role": "user",
    "content": patient_input
})

turns = 0
# Loop until a category is found
while True:
    # Generate a response from the model
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo-0613',
        # model="gpt-3.5-turbo-16k",
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

    # Print the assistant's reply
    print("Assistant:", assistant_reply)

    # Extract the predicted category from the assistant's final reply
    predicted_category = assistant.predict_category(assistant_reply)
    # Break the loop if a category has been found
    if predicted_category != "Unknown":
        break

    # Get additional patient input
    patient_input = input("Patient: ")

    # Add assistant and patient responses to the conversation
    assistant.messages.append({
        "role": "assistant",
        "content": assistant_reply
    })

    assistant.messages.append({
        "role": "user",
        "content": patient_input
    })

    # Increment the turn counter
    turns += 1

# Print the predicted category
print("Predicted category:", predicted_category)

print(f"Do you want to make an appointment with a {predicted_category} Medical Doctor? (y/n)")

appointment_or_not = input("Patient: ")

if appointment_or_not == 'n':
  print("goodbye")
else:
  doctor_recom = search_doctors(predicted_category, patient_address)
  dr_name = doctor_recom[0]
  err = 0
  while dr_name == 'error':
    if err > 2:
      print(f"Assistant:It seems the system has some issue, please drop this chat to find other way to solve your problem")
    print(f"Assistant: It seems that your address is not right, please input your address again.")
    new_address = input("Patient: ")
    doctor_recom = search_doctors(predicted_category, patient_address)
    err += 1
  dr_address = doctor_recom[1]
  print(f"""The clinic/doctor name is {dr_name}, \n
    whose address is \n 
    {dr_address}""")
  print(f"Assistant: You are going to receive a confirmation email about your appointment")
  subject = "Doctor Appoint confirmation"
  message = f"""{assistant_reply} \n
              The clinic/doctor's name is {dr_name}, whose address is {dr_address} \n
              at time: {patient_free_time}
              """
  send_email(sender_email, sender_password, receiver_email, subject, message)


print("Assistant: Goodbye!")





