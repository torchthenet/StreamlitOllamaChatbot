# -*- coding: utf-8 -*-
"""
ChatbotPages.py - Chatbot app for Ollama
Expanded Chatbot.py to hold multiple conversations at once.
Each conversation is on a different page, potentially with a different model.
"""

import logging
import streamlit as st
import ollama

# Moved most functions to another file to reduce clutter
# The moved functions either take no arguments or take specific arguments
# The functions remaining in this file all take a session dictionary as an argument
# This provides a simple way to assess function complexity
from ChatbotUtilities import (
        InitializeLogging,
        load_key,
        update_key,
        StreamData,
        SetSystemMessage,
        DisplayChatHistory,
        UpdateSessionLogs,
        RestoreSessionLogs,
        InventoryModels,
        ResetModel,
        ResetModule,
        DebuggingModule)

def GenerateNextResponse(session):
    """ Handle prompt submission
    Add the user's prompt to the messages list, then obtain and add the LLM response
    Save the metrics to the chatbot metrics list
    The LLM query includes the current temperature and context size
    """
    # Get all the keys from the session dictionary - even those we don't use
    messages_key=session['messages_key']
    metrics_key=session['metrics_key']
    system_key=session['system_key']
    prompt_key=session['prompt_key']
    temperature_key=session['temperature_key']
    context_key=session['context_key']
    model_key=session['model_key']
    old_model_key=session['old_model_key']
    session_log_key=session['session_log_key']
    metrics_log_key=session['metrics_log_key']
    # Append the user prompt to the messages list
    message={'role':'user',
             'content':st.session_state[prompt_key]
            }
    st.session_state[messages_key].append(message)
    # Get the model response and metrics
    response_metrics='metrics'
    stream=ollama.chat(
            model=st.session_state[model_key],
            messages=st.session_state[messages_key],
            options={'temperature':st.session_state[temperature_key],
                     'num_ctx':st.session_state[context_key]},
            stream=True)
    with st.expander(
                label='Response',
                expanded=True,
                icon=':material/smart_toy:'):
        response_text=st.write_stream(StreamData(stream,response_metrics,temperature_key,context_key,system_key))
    message={'role':'assistant',
            'content':response_text
            }
    st.session_state[messages_key].append(message)
    st.session_state[metrics_key].append(st.session_state[response_metrics])
    # Clear the prompt after it is successfully submitted
    st.session_state[prompt_key]=str()
    # Save the session and metrics logs
    UpdateSessionLogs(session_log_key,metrics_log_key,messages_key,metrics_key)
    st.rerun()

def ChatbotModule():
    """ The main chatbot module.
    Only when this module is selected will the sidebar show
    - Prompt edit mode
    - Clipboard mode
    """
    # Provide a toggle to enable editing the prompt
    editor_mode=st.sidebar.toggle(
            label='Prompt Edit Mode',
            value=False,
            help='Enable mode to simplify editing prompt entry.',
            key='editor_mode')
    copy_mode=st.sidebar.toggle(
            label='Clipboard Mode',
            value=False,
            help='Enable mode to add a copy to clipboard icon on messages.',
            key='clipboard_mode')

def MultiChatbotInterface():
    """ The main function for the single session chatbot interface."""
    # Define the keys used to store the session state values in a dictionary
    # This allows the same code to be used for mutli-session and single session chatbots
    # All of the single or first session keys start with 'cb_' to help identify them in the debugging module
    # Set up the main panel for the single session chatbot module
    st.markdown('### Multi Session Chatbot')
    st.divider()
    # Provide a list of pages to view
    # can't use shortcodes so copy and paste the images from
    # https://share.streamlit.io/streamlit/emoji-shortcodes
    # 1 = ":one:", 2 = ":two:", ...
    # debug = ":beetle:", reset = ":sparkles:"
    pages = {
        "Conversations": [
            st.Page(ChatOne, title='Chat One',icon='1️⃣'),
            st.Page(ChatTwo, title='Chat Two',icon='2️⃣'),
            st.Page(ChatThree, title='Chat Three',icon='3️⃣'),
        ],
        "Debugging": [
            st.Page(DebuggingModule, title='Debug',icon='🪲'),
            st.Page(ResetModule, title='Reset',icon='✨'),
        ],
    }
    pg = st.navigation(pages)
    pg.run()

def ChatOne():
    """ Page for chat number 1 """
    # Define the keys used to store the session state values in a dictionary
    # This allows the same code to be used for mutli-session and single session chatbots
    # All of the single or first session keys start with 'cb_' to help identify them in the debugging module
    session=dict()
    session['messages_key']='cb_messages'
    session['metrics_key']='cb_metrics'
    session['system_key']='cb_system'
    session['prompt_key']='cb_prompt'
    session['temperature_key']='cb_temperature'
    session['context_key']='cb_context'
    session['model_key']='cb_model'
    session['old_model_key']='cb_model_old'
    session['session_log_key']='cb_session_log_file'
    session['metrics_log_key']='cb_metrics_log_file'
    ChatbotModule()
    ChatbotSessionHandler(session)

def ChatTwo():
    """ Page for chat number 2 """
    # Define the keys used to store the session state values in a dictionary
    session=dict()
    session['messages_key']='c2_messages'
    session['metrics_key']='c2_metrics'
    session['system_key']='c2_system'
    session['prompt_key']='c2_prompt'
    session['temperature_key']='c2_temperature'
    session['context_key']='c2_context'
    session['model_key']='c2_model'
    session['old_model_key']='c2_model_old'
    session['session_log_key']='c2_session_log_file'
    session['metrics_log_key']='c2_metrics_log_file'
    ChatbotModule()
    ChatbotSessionHandler(session)

def ChatThree():
    """ Page for chat number 3 """
    # Define the keys used to store the session state values in a dictionary
    session=dict()
    session['messages_key']='c3_messages'
    session['metrics_key']='c3_metrics'
    session['system_key']='c3_system'
    session['prompt_key']='c3_prompt'
    session['temperature_key']='c3_temperature'
    session['context_key']='c3_context'
    session['model_key']='c3_model'
    session['old_model_key']='c3_model_old'
    session['session_log_key']='c3_session_log_file'
    session['metrics_log_key']='c3_metrics_log_file'
    ChatbotModule()
    ChatbotSessionHandler(session)

def ChatFour():
    """ Page for chat number 4 """
    # Define the keys used to store the session state values in a dictionary
    session=dict()
    session['messages_key']='c4_messages'
    session['metrics_key']='c4_metrics'
    session['system_key']='c4_system'
    session['prompt_key']='c4_prompt'
    session['temperature_key']='c4_temperature'
    session['context_key']='c4_context'
    session['model_key']='c4_model'
    session['old_model_key']='c4_model_old'
    session['session_log_key']='c4_session_log_file'
    session['metrics_log_key']='c4_metrics_log_file'
    ChatbotModule()
    ChatbotSessionHandler(session)

def ChatFive():
    """ Page for chat number 5 """
    # Define the keys used to store the session state values in a dictionary
    session=dict()
    session['messages_key']='c5_messages'
    session['metrics_key']='c5_metrics'
    session['system_key']='c5_system'
    session['prompt_key']='c5_prompt'
    session['temperature_key']='c5_temperature'
    session['context_key']='c5_context'
    session['model_key']='c5_model'
    session['old_model_key']='c5_model_old'
    session['session_log_key']='c5_session_log_file'
    session['metrics_log_key']='c5_metrics_log_file'
    ChatbotModule()
    ChatbotSessionHandler(session)

def ChatbotSessionHandler(session):
    # Define variables for each of the keys from the session dictionary
    # This makes reading the code easier and makes the multisession code cleaner
    messages_key=session['messages_key']
    metrics_key=session['metrics_key']
    system_key=session['system_key']
    prompt_key=session['prompt_key']
    temperature_key=session['temperature_key']
    context_key=session['context_key']
    model_key=session['model_key']
    old_model_key=session['old_model_key']
    session_log_key=session['session_log_key']
    metrics_log_key=session['metrics_log_key']
    # Set up the first row of buttons
    button_cols=st.columns(3,vertical_alignment='top')
    button_cols[0].markdown('Select Ollama Model')
    # Get a list of available ollama models for the selectbox
    model_list=list()
    for m in st.session_state['sys_models'].keys():
        model_list.append(m)
    # Allow user to select a model
    # This defaults to the first model
    # Ollama sorts the list by the most recently added or edited
    load_key(model_key)
    model=button_cols[0].selectbox(
            'Select Ollama model',
            model_list,
            label_visibility='collapsed',
            help='Select the model to use for the chatbot',
            key='_'+model_key,
            on_change=ResetModel,
            args=[model_key,old_model_key,system_key])
    if model_key not in st.session_state.keys():
        st.session_state[model_key]=model
    if old_model_key not in st.session_state.keys():
        st.session_state[old_model_key]=model
    # New Chat button
    button_cols[1].markdown('Start a new chat session')
    new_chat_btn=button_cols[1].button(
            'New Chat',
            help='Start a new chat',
            use_container_width=True)
    if new_chat_btn:
        if system_key in st.session_state.keys():
            del st.session_state[system_key]
        if messages_key in st.session_state.keys():
            del st.session_state[messages_key]
        if metrics_key in st.session_state.keys():
            del st.session_state[metrics_key]
        if session_log_key in st.session_state.keys():
            del st.session_state[session_log_key]
        if metrics_log_key in st.session_state.keys():
            del st.session_state[metrics_log_key]
        if prompt_key in st.session_state.keys():
            del st.session_state[prompt_key]
        st.rerun()
    # Restore Chat button
    button_cols[2].markdown('Restore a previous chat session')
    restore_chat_btn=button_cols[2].button(
            'Restore Chat',
            help='Restore a previous chat session',
            use_container_width=True)
    if restore_chat_btn:
        RestoreSessionLogs(messages_key,metrics_key)
    # Manage the system message
    SetSystemMessage(system_key,model_key)
    # Display the chat history if it exists
    DisplayChatHistory(messages_key,system_key,metrics_key)
    # Set up the second row of buttons
    # The submit button is only shown in editor mode
    if st.session_state['editor_mode'] == False:
        slider_cols=st.columns(2,vertical_alignment='center')
    else:
        slider_cols=st.columns(3,vertical_alignment='center')
        generate_btn=slider_cols[2].button(
                'Submit',
                help='Submit prompt to large language model',
                use_container_width=True)
    # Both options have the following two widgets.
    # Temperature Slider
    slider_cols[0].slider(
            label='Temperature',
            help='Adjust the randomness of the responses',
            value=0.1,
            min_value=0.0,
            max_value=1.0,
            step=0.1,
            key=temperature_key)
    # Context Size Slider
    model=st.session_state[model_key]
    max_context_size=st.session_state['sys_models'][model]['context_length']
    slider_cols[1].slider(
            label='Context token limit',
            help='Adjust the number of context tokens',
            value=2048,
            min_value=1024,
            max_value=max_context_size,
            step=1024,
            key=context_key)
    # There are two ways to get the user prompt:
    # 1. Use st.chat_input() to get the user prompt and submit it. This is the default.
    # 2. Use st.text_area() for more complex editing of the user prompt and submit it with a button.
    #
    if st.session_state['editor_mode'] == False:
        # Here is option 1 - using st.chat_input()
        # The st.chat_input always displays at the bottom of the screen.
        # Pressing return submits the prompt, which makes it impossible to structure a prompt with context.
        if chatbot_prompt:=st.chat_input():
            st.session_state[prompt_key]=chatbot_prompt
            GenerateNextResponse(session)
    else:
        # This is option 2 - using st.text_area()
        # With this option there should be a submit button to generate the response.
        if generate_btn:
            GenerateNextResponse(session)
        # Provide an editable text box for the next prompt
        # This block uses st.text_area instead.
        if prompt_key not in st.session_state:
            st.session_state[prompt_key]=str()
        load_key(prompt_key)
        with st.expander(
                    label="Enter your question here:",
                    expanded=True,
                    icon=':material/person:'):
            chatbot_prompt=st.text_area(
                    label='Question',
                    label_visibility='collapsed',
                    placeholder='Enter your question here',
                    key="_"+prompt_key,
                    height=100,
                    on_change=update_key,
                    args=[prompt_key])

if __name__=='__main__':
    # The application itself.
    # Set up the Streamlit web page, start logging (not part of Streamlit),
    # create the list of available models for each chat to choose from,
    # create menu of pages in the sidebar for chats and debugging pages.
    
    # See https://docs.streamlit.io/develop/api-reference/configuration/st.set_page_config
    # Choose page icon from one of the following:
    #  https://share.streamlit.io/streamlit/emoji-shortcodes
    #  https://fonts.google.com/icons?icon.set=Material+Symbols&icon.style=Rounded 
    st.set_page_config(
            page_title='Chatbot',
            page_icon=':robot_face:',
            layout='wide',
            initial_sidebar_state='expanded',
            menu_items={
                    'Get Help': None,
                    'Report a bug': None,
                    'About': '# Ollama Chatbot Pages' 
                    } )
    # set up logging to a log file and the console
    if 'log' not in st.session_state:
        st.session_state['log']=logging.getLogger()
        InitializeLogging()
    # Inventory available Ollama models, adding features/parameters to st.session_state
    # This should only run once as the results are cached using @st.cache_data.
    InventoryModels()
    # Set up the sidebar with a title and a list of pages to view
    st.sidebar.header('Ollama Chatbot')
    # Provide a list of pages to view
    # can't use shortcodes so copy and paste the images from
    # https://share.streamlit.io/streamlit/emoji-shortcodes
    # 1 = ":one:", 2 = ":two:", ...
    # debug = ":beetle:", reset = ":sparkles:"
    pages = {
        "Conversations": [
            st.Page(ChatOne, title='Chat One',icon='1️⃣'),
            st.Page(ChatTwo, title='Chat Two',icon='2️⃣'),
            st.Page(ChatThree, title='Chat Three',icon='3️⃣'),
            st.Page(ChatFour, title='Chat Four',icon='4️⃣'),
            st.Page(ChatFive, title='Chat Five',icon='5️⃣'),
        ],
        "Debugging": [
            st.Page(DebuggingModule, title='Debug',icon='🪲'),
            st.Page(ResetModule, title='Reset',icon='✨'),
        ],
    }
    pg = st.navigation(pages)
    pg.run()

# vim: set expandtab tabstop=4 shiftwidth=4 autoindent: