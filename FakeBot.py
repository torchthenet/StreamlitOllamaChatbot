""" FakeBot from the Streamlit tutorial at:
https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps

Exanded the response list.
"""
import streamlit as st
import random
import time


# Streamed response emulator
def response_generator():
    response = random.choice(
        [
            "Hello there! How can I assist you today?",
            "Hi, human! Is there anything I can help you with?",
            "Do you need help?",
            "Perhaps if you explain yourself a little more.",
            "As a Large Language Model, I'm unable to assist you with that.",
            "Sometimes it helps to rephrase the question.",
            "I am not your therapist and cannot assist you with that request.",
            "Have you tried turning it off and back on again?",
        ]
    )
    for word in response.split():
        yield word + " "
        time.sleep(0.05)


if __name__ == "__main__":
    # See https://docs.streamlit.io/develop/api-reference/configuration/st.set_page_config
    # Choose a page icon from https://share.streamlit.io/streamlit/emoji-shortcodes
    # Or from https://fonts.google.com/icons?icon.set=Material+Symbols&icon.style=Rounded 
    st.set_page_config(
        page_title="FakeBot",
        page_icon=":game_die:",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': None,
            'Report a bug': None,
            'About': "# Fake Bot. Not a real bot."
        }
    )
    st.title("Fake Bot")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("What is up?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            response = st.write_stream(response_generator())
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})