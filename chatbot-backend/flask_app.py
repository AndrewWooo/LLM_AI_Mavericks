from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

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

if __name__ == "__main__":
    app.run(port=5010)
