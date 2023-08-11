import os
import openai
from fuzzywuzzy import fuzz

from serpapi import GoogleSearch
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

import smtplib
import ssl
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


serpapi_key = os.environ.get('SERPAPI_KEY')
api_key = os.environ.get('OPENAI_API_KEY')
openai.api_key = api_key

sender_email = os.environ.get('SENDER_EMAIL')
sender_password = os.environ.get('SENDER_PIN')

def send_email(receiver_email, subject, message):
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
    
    return 'success'

   

def do_geocode(address):
    geopy = Nominatim(user_agent="app")
    try:
        return geopy.geocode(address, timeout=10)
    except GeocoderTimedOut:
        return do_geocode(address)

def do_googleSearch(params):
    try:
        search = GoogleSearch(params)
        return search.get_dict()
    except Exception as e:
        return {"error": str(e)}
    
"""
 Returns are the doctor's name and address, both are strings. \
    use this when the agent want to help user to make an appointment with a doctor and \
    after the user provide the one's address, \
    The inputs are two variables, first one is doctorType: str, \
    second one is address: str.\
    it also return errors if Missing required parameters \
    or Geocoding failed. Invalid address or API error
"""        
def search_doctors(doctorType: str, address: str):
    top_k = 1
    if not doctorType or not address:
      return 'error', 'Missing required parameters.'
        # return jsonify({'error': 'Missing required parameters.'}), 400
    # Initialize Nominatim API
    #geolocator = Nominatim(user_agent="MyApp")
    # address = "14449 south quiet shade dr, herriman, ut 84096"
    location = do_geocode(address)   # modify this line, catch error
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
        #search = GoogleSearch(params)
        #results = search.get_dict()
        results = do_googleSearch(params) # modify this line, catch error
        doctors = []
        for result in results['local_results'][:top_k]:
            name = result['title']
            address = result['address']
            doctors.append({'name': name, 'address': address})
        return doctors[0]['name'], doctors[0]['address']
    else:
        return 'error', 'Geocoding failed. Invalid address or API error.'

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
            'Pulmonologist',
            "psychologist", 
            'psychiatrist',
            'rheumatologist',
            'endocrinologist',
            'ophthalmologist'
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
            'Pulmonologist': 'Pulmonology',
            'psychologist': 'psychology',
            'psychiatrist': 'psychiatry',
            'rheumatologist': 'rheumatology',
            'endocrinologist': 'endocrinology',
            'ophthalmologist': 'ophthalmology'
        }
        system_message = """
        You are a medical AI assistant. Your role is to suggest the appropriate type of doctor for the patient to see based on their details and symptoms. When diagnosing, remember to think step by step, first gathering the patient's symptoms, considering potential causes, asking follow-up questions if necessary, and only then making your suggestion. Use simple, non-medical language that a layperson can understand.
        If at any point during the conversation, the patient describes symptoms of a medical emergency, please immediately end the chat and advise the patient to call 911 or their local emergency number. Safety is our top priority, and emergencies require immediate medical attention.
        Additionally, please provide a rationale for your recommendation, explaining why you picked a specific category of doctor for the patient.
        Last but not least, if the customer's input is unclear or does not make sense, politely ask them to provide more specific or clearer information.
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
        predicted_category = self.categories[0]  # Default category
        for keyword, category in self.category_mapping.items():
            ratio = fuzz.token_set_ratio(keyword, user_input.lower())
            if ratio > max_ratio:
                max_ratio = ratio
                predicted_category = category
        return predicted_category if max_ratio > 80 else "Unknown"

#init the assistant object
assistant = DoctorCategoryAssistant()

def addSystemMessage(gender, age, smoke, medical_records):
    # System message
    assistant.messages.append({"role": "system", "content": assistant.logic})
    assistant.messages.append({"role": "system", "content": f"Patient Gender: {gender}"})
    assistant.messages.append({"role": "system", "content": f"Patient Age: {age}"})
    assistant.messages.append({"role": "system", "content": f"smoke or not: {smoke}"})
    assistant.messages.append({"role": "system", "content": f"Patient Medical Records: {medical_records}"})


def get_response(msg):
    """Returns the assistant's response to the user's message"""
    # Add the user's message to the conversation
    #prompt = f'{chat_log}user: {msg}\nassistant:'
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
    replyRaw =response.choices[0].message['content']
    # replace line break
    assistant_reply = replyRaw.replace("\n", "<br>")
    
    # Add the assistant's reply to the conversation
    assistant.messages.append({
        "role": "assistant",
        "content": assistant_reply
    })
    # Extract the predicted category from the assistant's final reply
    predicted_category = assistant.predict_category(assistant_reply)
    if predicted_category != "Unknown":
        tmpMsg="Do you want to make an appt. with a [" + predicted_category+ "] Medical Doctor? (y/n)"
        return {'reply':assistant_reply, 'category':predicted_category, 'followMsg':tmpMsg}
    return {'reply':assistant_reply}

