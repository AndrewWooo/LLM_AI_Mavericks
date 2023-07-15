import os
import json
import openai
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


patient_form = {'receiver_email' :'ray.jianlei.zhang@gmail.com',
'patient_address' : "2204 New College Ln, Plano, TX 75025",
'patient_free_time' : "today at 3:00pm CDT"
}
receiver_email = patient_form['receiver_email']
patient_address = patient_form['patient_address']

patient_free_time = patient_form['patient_free_time']


# Create an instance of the DoctorCategoryAssistant class
assistant = DoctorCategoryAssistant()

script_dir = os.path.dirname(os.path.abspath(__name__))
# Load patient information from a JSON file
# print('script_dir', script_dir)
with open(f'{script_dir}/patient_1.json') as f:
    patient_info = json.load(f)

# Extract patient details
# patient_description = patient_info['description']
smoke = patient_info['smoke']
age = patient_info['age']
gender = patient_info['gender']
medical_records = patient_info['medical_records']

# System message
assistant.messages.append({"role": "system", "content": assistant.logic})
# assistant.messages.append({"role": "system", "content": f"Patient Description: {patient_info['description']}"})
assistant.messages.append({"role": "system", "content": f"smoke or not: {patient_info['smoke']}"})
assistant.messages.append({"role": "system", "content": f"Patient Age: {patient_info['age']}"})
assistant.messages.append({"role": "system", "content": f"Patient Gender: {patient_info['gender']}"})
assistant.messages.append({"role": "system", "content": f"Patient Medical Records: {patient_info['medical_records']}"})

# print("Assistant: Hello, what brought you here today?")
jsonify({"assistant_reply": "Hello, what brought you here today?"})
# patient_input = input("Patient: ")
patient_input = request.json['patient_input']
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
    # print("Assistant:", assistant_reply)
    jsonify({"assistant_reply": assistant_reply})

    # Extract the predicted category from the assistant's final reply
    predicted_category = assistant.predict_category(assistant_reply)
    # Break the loop if a category has been found
    if predicted_category != "Unknown":
        break

    # Get additional patient input
    # patient_input = input("Patient: ")
    patient_input = request.json['patient_input']

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

# print(f"Do you want to make an appointment with a {predicted_category} Medical Doctor? (y/n)")
jsonify({"assistant_reply": f"Do you want to make an appointment with a {predicted_category} Medical Doctor? (y/n)"})


assistant_reply
# appointment_or_not = input("Patient: ")
patient_input = request.json['patient_input']

if appointment_or_not == 'n':
  # print("goodbye")
  jsonify({"assistant_reply": "Since you do not need appointment. It is time to say Goodbye"})
else:
  doctor_recom = search_doctors(predicted_category, patient_address)
  dr_name = doctor_recom[0]
  err = 0
  while dr_name == 'error':
    if err > 2:
      # print(f"Assistant:It seems the system has some issue, please drop this chat to find other way to solve your problem")
      jsonify({"assistant_reply": f"Assistant:It seems the system has some issue, please drop this chat to find other way to solve your problem"})
    # print(f"Assistant: It seems that your address is not right, please input your address again.")
    jsonify({"assistant_reply": "It seems that your address is not right, please input your address again."})
    # new_address = input("Patient: ")
    patient_input = request.json['patient_input']
    doctor_recom = search_doctors(predicted_category, patient_address)
    err += 1
  dr_address = doctor_recom[1]
  # print(f"""The clinic/doctor name is {dr_name}, \n
  #   whose address is \n 
  #   {dr_address}""")
  jsonify({"assistant_reply": f"""The clinic/doctor name is {dr_name}, \n
    whose address is \n 
    {dr_address}"""})
  # print(f"Assistant: You are going to receive a confirmation email about your appointment")
  jsonify({"assistant_reply": "You are going to receive a confirmation email about your appointment"})
  subject = "Doctor Appoint confirmation"
  message = f"""{assistant_reply} \n
              The clinic/doctor's name is {dr_name}, whose address is {dr_address} \n
              at time: {patient_free_time}
              """
  send_email(sender_email, sender_password, receiver_email, subject, message)

jsonify({"assistant_reply": "You are all set. Goodbye!"
# print("Assistant: Goodbye!")





