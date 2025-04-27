# -*- coding: utf-8 -*-
"""
Wrote this to debug the system_key not updating in Chatbot.py
This works as expected.
Every instance of system_key, _system_key, and system_message are the same.
Lessons learned:
- This works because the widget is continuously rendered.
- Commenting out the last 3 lines doesn't matter.
= = =
The issue is the on_change call in model=st.sidebar.selectbox
"""
import streamlit as st

def load_key(key):
    st.session_state["_"+key] = st.session_state[key]

def update_key(key):
    st.session_state[key] = st.session_state["_"+key]

system_key='cb_system'

if system_key not in st.session_state.keys():
    st.session_state[system_key]="This is a test message."
    st.write('added system_key to session_state')
    st.write('system_key = '+st.session_state[system_key])
else:
    st.write('system_key in session_state')
    st.write('system_key = '+st.session_state[system_key])

load_key(system_key)
system_message=st.text_area(
    label='System Message',
    label_visibility='visible',
    key="_"+system_key,
    height=68,
    on_change=update_key,
    args=[system_key])
st.write('system_message = '+system_message)
st.write('system_key = '+st.session_state[system_key])
st.write('_system_key = '+st.session_state["_"+system_key])