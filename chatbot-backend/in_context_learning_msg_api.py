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

#api_key = os.environ.get('OPENAI_API_KEY')
openai.api_key = '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'
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
