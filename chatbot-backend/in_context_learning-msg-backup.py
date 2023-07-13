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

serpapi_key = os.environ.get('SERPAPI_KEY')


api_key = os.environ.get('OPENAI_API_KEY')

sender_email = os.environ.get('SENDER_EMAIL')
sender_password = os.environ.get('SENDER_PIN')

openai.api_key = api_key

app = Flask(__name__)

def search_doctors(doctorType: str, address: str):
    """Returns are the doctor's name and address, both are strings. \
    use this when the agent want to help user to make an appointment with a doctor and \
    after the user provide the one's address, \
    The inputs are two variables, first one is doctorType: str, \
    second one is address: str.\
    it also return errors if Missing required parameters \
    or Geocoding failed. Invalid address or API error"""
    top_k = 1
    if not doctorType or not address:
      return 'error', 'Missing required parameters.'
        # return jsonify({'error': 'Missing required parameters.'}), 400
    # Initialize Nominatim API
    geolocator = Nominatim(user_agent="MyApp")
    # address = "14449 south quiet shade dr, herriman, ut 84096"
    location = geolocator.geocode(address)
    if location:
        latitude = location.latitude
        longitude = location.longitude
        params = {
            "api_key": serpapi_key,
            "engine": "google_maps",
            "type": "search",
            "google_domain": "google.com",
            "q": doctorType,
            "hl": "en",
            "ll": f"@{latitude},{longitude},14z"
        }
        search = GoogleSearch(params)
        results = search.get_dict()
        doctors = []
        for result in results['local_results'][:top_k]:
            name = result['title']
            address = result['address']
            doctors.append({'name': name, 'address': address})
        return doctors[0]['name'], doctors[0]['address']
    else:
        return 'error', 'Geocoding failed. Invalid address or API error.'


def send_email(sender_email, sender_password, receiver_email, subject, message):
    # Set up the SMTP server
    smtp_server = 'smtp-mail.outlook.com'
    smtp_port = 587
    # Create a multipart message
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject

    # Add the message body
    msg.attach(MIMEText(message, "plain"))


    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        # server.starttls(context=ssl.create_default_context())
        server.login(sender_email, sender_password)
        server.send_message(msg)


class DoctorCategoryAssistant:
    def __init__(self):

        self.categories = [
            "General Practitioner",
            "Cardiologist",
            "Dermatologist",
            "Pediatrics",
            "Neurologist",
            "Orthopedic Surgeon",
            "Radiologist",
            "Gastroenterologist",
            "Oncologist",
            'Pulmonologist'
        ]

        self.category_mapping = {
            "general practitioner": "General Practice or Family Medicine",
            "cardiologist": "Cardiology",
            "dermatologist": "Dermatology",
            "pediatrician": "Pediatrics",
            "neurologist": "Neurology",
            "orthopedic surgeon": "Orthopedics",
            "radiologist": "Radiology",
            "gastroenterologist": "Gastroenterology",
            "oncologist": "Oncology",
            'Pulmonologist': 'Pulmonology'
        }
        system_message = """
        You are a medical AI assistant. Your role is to suggest the appropriate type of doctor for the patient to see based on their details and symptoms.
        When diagnosing, remember to think step by step, first gathering the patient's symptoms, considering potential causes, asking follow-up questions if necessary, and only then making your suggestion. 
        Also, use simple, non-medical language that a layperson can understand.

        list of retionale, why this category..
        """
        self.messages = [{
            "role": "system",
            "content": system_message
        }]

        self.logic = """
        - Please provide the following physical information to navigate to the appropriate doctor category:
          - Ask for patient's age.
          - Ask for patient's gender (Male/Female/Other).
          - Ask if the patient is a smoker (Yes/No).
          - Ask if the patient has any significant medical records (Yes/No).
        - If the patient is under 18:
          - Direct the patient to the Pediatrics department.
        - If the patient is a smoker:
          - Advise the patient to visit a General Practitioner for a check-up and advice on smoking cessation.
        - If the patient is not a smoker:
          - If the patient is female:
            - If the patient has significant medical records:
              - Direct the patient to a Gynecologist/Obstetrician.
            - If the patient does not have significant medical records:
              - Direct the patient to a General Practitioner.
          - If the patient is male:
            - If the patient has significant medical records:
              - Direct the patient to a Urologist.
            - If the patient does not have significant medical records:
              - Direct the patient to a General Practitioner.
          - If the patient is neither female nor male:
            - Ask if the patient has any skin-related symptoms.
              - If yes:
                - Direct the patient to a Dermatologist.
              - If no:
                - Ask if the patient has any heart-related symptoms.
                  - If yes:
                    - Direct the patient to a Cardiologist.
                  - If no:
                    - Ask if the patient has any neurological symptoms.
                      - If yes:
                        - Direct the patient to a Neurologist.
                      - If no:
                        - Ask if the patient has any bone or joint-related symptoms.
                          - If yes:
                            - Direct the patient to an Orthopedic Surgeon.
                          - If no:
                            - Ask if the patient has any gastrointestinal symptoms.
                              - If yes:
                                - Direct the patient to a Gastroenterologist.
                              - If no:
                                - Ask if the patient has any cancer-related symptoms.
                                  - If yes:
                                    - Direct the patient to an Oncologist.
                                  - If no:
                                    - Direct the patient to a General Practitioner.
        """
    def predict_category(self, user_input):
        max_ratio = -1
        predicted_category = self.categories[-1]  # Default category
        for keyword, category in self.category_mapping.items():
            ratio = fuzz.token_set_ratio(keyword, user_input.lower())
            if ratio > max_ratio:
                max_ratio = ratio
                predicted_category = category
        return predicted_category if max_ratio > 70 else "Unknown"


# Create an instance of the DoctorCategoryAssistant class
assistant = DoctorCategoryAssistant()

script_dir = os.path.dirname(os.path.abspath(__name__))
# Load patient information from a JSON file
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
patient_address = "2204 New College Ln, Plano, TX 75025"

if appointment_or_not == 'n':
  print("goodbye")
else:
  doctor_recom = search_doctors(predicted_category, patient_address)
  dr_name = doctor_recom[0]
  dr_address = doctor_recom[1]
  print(f"Your doctor name is {dr_name}, whose address is {dr_address}")

print(f"you are going to receive a confirmation email")

patient_dr_time = "today at 3:00pm CDT"
subject = "Doctor Appoint confirmation"
message = f"""{assistant_reply} \n
            Your doctor name is {dr_name}, whose address is {dr_address} \n
            at time: {patient_dr_time}
            """

receiver_email = 'ray.jianlei.zhang@gmail.com'

send_email(sender_email, sender_password, receiver_email, subject, message)








