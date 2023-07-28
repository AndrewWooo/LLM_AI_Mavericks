import openai
import streamlit as st

st.title("Welcome to Mavericks")

openai.api_key = st.secrets["OPENAI_API_KEY"]

# Add Two Buttons
col1, col2 = st.columns(2)

# Add "Reset Chat" button
with col1:
    if st.button("Reset Chat"):
        st.session_state.messages = []
    
# Add "Save Chat" button
with col2:
    if st.button("Save Chat"):
        messages = st.session_state.messages;
        if messages:
            last_index = len(messages) - 1
            print(messages[last_index]["content"])

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What can I help you today?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for response in openai.ChatCompletion.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        ):
            full_response += response.choices[0].delta.get("content", "")
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    # print(st.session_state.messages)
    
    # st.session_state.messages = [
    # {"role": "user", "content": "Hi, can you help me find a doctor?"},
    # {"role": "assistant", "content": "Sure, I can help you find a doctor."},
    # {"role": "user", "content": "I need a dentist near my location."},
    # {"role": "assistant", "content": "Sure, let me find a dentist nearby."},
    # {"role": "assistant", "content": "Here are some dentists in your area:"},
    # {"role": "assistant", "content": "- Dentist A"},
    # {"role": "assistant", "content": "- Dentist B"},
    # # ... more messages ...
    # ]
