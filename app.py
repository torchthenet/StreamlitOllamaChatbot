#https://docs.streamlit.io/develop/api-reference/navigation/st.navigation
import streamlit as st

def create_account():
    st.header('Create Account')

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

def learn():
    st.header('Learn')

def trial():
    st.header('Trial')

pages = {
    "Your account": [
        st.Page(create_account, title="Create your account",icon=":material/favorite:"),
        st.Page(manage_account, title="Manage your account"),
    ],
    "Resources": [
        st.Page(learn, title="Learn about us"),
        st.Page(trial, title="Try it out"),
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