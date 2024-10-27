# -*- coding: utf-8 -*-
""" Demonstrate and test different Streamlit features
"""
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

def demo():
    """ Demo and test Streamlit components
    """
    st.header('Demo')
    # https://docs.streamlit.io/develop/api-reference/status
    button_cols=st.columns(5,vertical_alignment='center')
    success_btn=button_cols[0].button(
            'Success',
            help="Demonstrate the success callout",
            use_container_width=True)
    info_btn=button_cols[1].button(
            'Info',
            help="Demonstrate the info callout",
            use_container_width=True)
    warn_btn=button_cols[2].button(
            'Warn',
            help="Demonstrate the warn callout",
            use_container_width=True)
    err_btn=button_cols[3].button(
            'Error',
            help="Demonstrate the error callout",
            use_container_width=True)
    exception_btn=button_cols[4].button(
            'Exception',
            help="Demonstrate the exception callout",
            use_container_width=True)
    if success_btn:
        st.success('A :blue[success] message!',icon=':material/thumb_up:')
    if info_btn:
        st.info('An :green[info] message!',icon=':material/info:')
    if warn_btn:
        st.warning('A :orange[warn] message!',icon=':material/warning:')
    if err_btn:
        st.error('An :red[error] message!',icon=':material/report:')
    if exception_btn:
        st.exception('This is an exception message!')
    # https://docs.streamlit.io/develop/api-reference/layout
    button_cols=st.columns(5,vertical_alignment='center')
    modal_btn=button_cols[0].button(
            'Modal Dialog',
            help="Demonstrate a modal dialog",
            use_container_width=True)
    popover_btn=button_cols[1].button(
            'Popover',
            help="Demonstrate a popover",
            use_container_width=True)
    toast_btn=button_cols[2].button(
            'Toast',
            help="Demonstrate a toast",
            use_container_width=True)
    if modal_btn:
        DemonstrationDialog()
    if popover_btn:
        with st.popover('Demonstrate Popover',help='This is a popover'):
            st.write(':blue[Popover] message')
    if toast_btn:
        st.toast('This is a :red[toast]!',icon=':material/bolt:')

@st.dialog('Demonstration Dialog')
def DemonstrationDialog():
    st.write('Press :red[Close]')
    if st.button('Close'):
        st.rerun()

# can't use shortcodes so copy and paste the images from
# https://share.streamlit.io/streamlit/emoji-shortcodes
# 1 = ":one:", 2 = ":two:", ...
# debug = ":beetle:", reset = ":sparkles:"
# Or use Google Material font (limited to b&w)
pages = {
    "Your account": [
        st.Page(create_account, title="Create your account",icon=":material/favorite:"),
        st.Page(manage_account, title="Manage your account"),
    ],
    "Resources": [
        st.Page(learn, title="Learn about us"),
        st.Page(demo, title="Demonstrations"),
    ],
}

# See https://docs.streamlit.io/develop/api-reference/configuration/st.set_page_config
# Choose page icon from one of the following:
#  https://share.streamlit.io/streamlit/emoji-shortcodes
#  https://fonts.google.com/icons?icon.set=Material+Symbols&icon.style=Rounded 
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

# vim: set expandtab tabstop=4 shiftwidth=4 autoindent: