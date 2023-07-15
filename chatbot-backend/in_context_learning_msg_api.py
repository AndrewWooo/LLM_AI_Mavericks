import os
import json
import openai
from fuzzywuzzy import fuzz
# api 
from flask import Flask
"""
from serpapi import GoogleSearch
import requests
from geopy.geocoders import Nominatim

import smtplib
import ssl
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
"""
from backend_utilities import *

api_key = os.environ.get('OPENAI_API_KEY')
openai.api_key = api_key
"""
serpapi_key = os.environ.get('SERPAPI_KEY')
sender_email = os.environ.get('SENDER_EMAIL')i
sender_password = os.environ.get('SENDER_PIN')
"""

app = Flask(__name__)

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
receiver_email = patient_info['receiver_email']
patient_address = patient_info['patient_address']
patient_free_time = patient_info['patient_free_time']


# System message
assistant.messages.append({"role": "system", "content": assistant.logic})
# assistant.messages.append({"role": "system", "content": f"Patient Description: {patient_info['description']}"})
assistant.messages.append({"role": "system", "content": f"smoke or not: {patient_info['smoke']}"})
assistant.messages.append({"role": "system", "content": f"Patient Age: {patient_info['age']}"})
assistant.messages.append({"role": "system", "content": f"Patient Gender: {patient_info['gender']}"})
assistant.messages.append({"role": "system", "content": f"Patient Medical Records: {patient_info['medical_records']}"})


def get_response(msg):
    """Returns the assistant's response to the user's message"""

    # Add the user's message to the conversation
    assistant.messages.append({
        "role": "user",
        "content": msg
    })
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
    # Add the assistant's reply to the conversation
    assistant.messages.append({
        "role": "assistant",
        "content": assistant_reply
    })
    # Extract the predicted category from the assistant's final reply
    predicted_category = assistant.predict_category(assistant_reply)
    if predicted_category != "Unknown":
        categoryFinded = True
        choose_doctor="Do you want to make an appt. with a [" + predicted_category+ "] Medical Doctor? (y/n)"
        return choose_doctor
    else:
        return assistant_reply



           
       

if __name__ == "__main__":
    print("Assistant: Hello, what brought you here today? (type 'quit' to exit)")
    while True:
        # sentence = "do you use credit cards?"
        sentence = input("You: ")
        if sentence == "quit":
            break

        resp = get_response(sentence)
        print(resp)

"""

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

jsonify({"assistant_reply": "You are all set. Goodbye!"})
# print("Assistant: Goodbye!")
"""