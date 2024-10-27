#https://docs.streamlit.io/develop/api-reference/navigation/st.navigation
import streamlit as st

def chat_one():
    st.header('First Chat')

def chat_two():
    st.header('Second Chat')

def chat_three():
    st.header('Third Chat')

def chat_four():
    st.header('Fourth Chat')

def chat_five():
    st.header('Fifth Chat')

def manage_account():
    st.header('Manage Account')
    tab1, tab2, tab3 = st.tabs(["Cat", "Dog", "Owl"])
    with tab1:
        st.header("A cat")
        st.image("https://static.streamlit.io/examples/cat.jpg", width=200)
    with tab2:
        st.header("A dog")
        st.image("https://static.streamlit.io/examples/dog.jpg", width=200)
    with tab3:
        st.header("An owl")
        st.image("https://static.streamlit.io/examples/owl.jpg", width=200)

def debug():
    st.header('Debug')

def reset():
    st.header('Reset')

# 
pages = {
    "Conversations": [
        st.Page(chat_one, title="Chat One",icon="1️⃣"),
        st.Page(chat_two, title="Chat Two",icon="2️⃣"),
        st.Page(chat_three, title="Chat Three",icon="3️⃣"),
        st.Page(chat_four, title="Chat Four",icon="4️⃣"),
        st.Page(chat_five, title="Chat Five",icon="5️⃣"),
    ],
    "Debugging": [
        st.Page(debug, title="Debug App"),
        st.Page(reset, title="Reset App"),
    ],
}

st.set_page_config(
        page_title='Navigation',
        page_icon=':material/smart_toy:',
        layout='wide',
        initial_sidebar_state='expanded',
        menu_items={
                'Get Help': None,
                'Report a bug': None,
                'About': None,
                } )
pg = st.navigation(pages)
pg.run()