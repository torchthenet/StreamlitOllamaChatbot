# -*- coding: utf-8 -*-
"""
Chatbot.py - Basic chatbot app for Ollama
"""

import os
import sys
import logging
import streamlit as st
import ollama
import time


def StreamData(stream):
    """ The Ollama generator is not compatible with st.write_stream
    This wrapper is compatible.
    Only the final response returns the metrics.
    """
    for chunk in stream:
        if chunk['done']:
            st.session_state['metrics']=chunk.copy()
        else:
            yield chunk['message']['content']

def DisplayMetrics(metrics):
    metrics_string='Model: '+metrics['model']
    metrics_string+='\nPrompt tokens = '+str(metrics['prompt_eval_count'])
    metrics_string+='\nResponse tokens = '+str(metrics['eval_count'])
    milliseconds=metrics['total_duration']/1000000
    seconds=round(milliseconds/1000,2)
    metrics_string+='\nDuration (seconds) = '+str(seconds)
    with st.expander(
                label='Response Metrics',
                expanded=True,
                icon=':material/stylus:'):
        st.text(metrics_string)

def SetSystemMessage():
    """ By convention (and maybe necessity) the system message is the first
    message in the conversation, and there is only one of them. If the user
    deletes the system message then delete the first message. If the use edits
    or keeps the default system message, then store that as the first message.
    The chatbot system message persists in the cb_system key.
    """
    if 'cb_system' not in st.session_state:
        today=time.strftime('%A, %B %d, %Y')
        st.session_state['cb_system']=f'Today is {today}.'
    system_message=st.text_area(
            label='System message',
            label_visibility='visible',
            key='cb_system',
            height=100)

def CheckSystemMessage():
    """ Manage the system message. If this module has just started then
    add the system message to the messages list. If the user edits the system
    message then update it. If the user deletes the content then remove it.
    """
    # If the system message is blank then delete the system message
    if len(st.session_state['cb_system'])==0:
        if len(st.session_state['cb_messages'])>0:
            if st.session_state['cb_messages'][0]['role']=='system':
                del st.session_state['cb_messages'][0]
    else:
        # create the system message
        message={'role':'system',
                 'content':st.session_state['cb_system']
                }
        if st.session_state['cb_messages']:
            # if there are messages then the system message is placed first
            if st.session_state['cb_messages'][0]['role']=='system':
                # easier to just replace the message than check if it changed
                st.session_state['cb_messages'][0]=message
            else:
                st.session_state['cb_messages'].insert(0,message)
        else:
            # if there are no message then append the system message
            st.session_state['cb_messages'].append(message)

def DisplayChatHistory():
    """ Display the chat history if there is one. Each message is placed in a
    box with an icon and role name. Every response message is followed by the
    metrics from that query and response.
    If this module has just launched then create empty lists to fill in later.
    """
    if 'cb_messages' not in st.session_state:
        st.session_state['cb_messages']=list()
        st.session_state['cb_metrics_list']=list()
    CheckSystemMessage()
    if len(st.session_state['cb_messages']):
        j=0
        for msg in st.session_state['cb_messages']:
            match msg['role']:
                case 'user':
                    label='Question'
                    icon=':material/person:'
                case 'assistant':
                    label='Response'
                    icon=':material/smart_toy:'
                case 'system':
                    label='System'
                    icon=':material/psychology:'
                case _:
                    label=msg['role']
                    icon=':material/stylus:'
            with st.expander(
                        label=label,
                        expanded=True,
                        icon=icon):
                st.write(msg['content'])
            if msg['role']=='assistant':
                DisplayMetrics(st.session_state['cb_metrics_list'][j])
                j+=1
    st.divider()

def GenerateNextResponse():
    """ Handle the generate response button. First, add the user's prompt
    to the messages list, then obtain and add the LLM response. Also, save
    the metrics to the chatbot metrics list.
    The LLM query includes the current temperature.
    Call st.rerun to force display of the user prompt in a non-editable way.
    """
    message={'role':'user',
             'content':st.session_state['chatbot_prompt']
            }
    st.session_state['cb_messages'].append(message)
    stream=ollama.chat(
            model=st.session_state['model'],
            messages=st.session_state['cb_messages'],
            options={'temperature':st.session_state['cb_temperature']},
            stream=True)
    with st.expander(
                label='Response',
                expanded=True,
                icon=':material/smart_toy:'):
        response_text=st.write_stream(StreamData(stream))
    message={'role':'assistant',
            'content':response_text
            }
    st.session_state['cb_messages'].append(message)
    st.session_state['cb_metrics_list'].append(st.session_state['metrics'])
    st.rerun()

def ChatbotModule():
    SetSystemMessage()
    # Display the chat history if it exists
    DisplayChatHistory()
    # Provide an editable text box for the next prompt
    # the st.chat_input always displays at the bottom of the screen
    # Pressing return submits the prompt, which makes it hard to structure
    # a prompt with context.
    # Switching this back to st.text_area instead.
    # if chatbot_prompt:=st.chat_input():
    #     st.session_state['chatbot_prompt']=chatbot_prompt
    #     GenerateNextResponse()
    if 'chatbot_prompt' not in st.session_state:
        st.session_state['chatbot_prompt']='Enter your prompt here'
    with st.expander(
                label="Question",
                expanded=True,
                icon=':material/person:'):
        chatbot_prompt=st.text_area(
                label='Question',
                label_visibility='collapsed',
                value=st.session_state['chatbot_prompt'],
                height=100)
    st.session_state['chatbot_prompt']=chatbot_prompt
    button_cols=st.columns((1,2,1),vertical_alignment='center')
    new_chat_btn=button_cols[0].button(
            'New Chat',
            help='Start a new chat',
            use_container_width=True)
    button_cols[1].slider(
            label='Temperature',
            value=0.1,
            min_value=0.0,
            max_value=1.0,
            step=0.1,
            key='cb_temperature')
    generate_btn=button_cols[2].button(
            'Submit',
            help='Submit prompt to large language model',
            use_container_width=True)
    if new_chat_btn:
        del st.session_state['cb_system']
        del st.session_state['cb_messages']
        del st.session_state['cb_metrics_list']
        st.rerun()
    if generate_btn:
        GenerateNextResponse()

def DebuggingModule():
    st.write('## Debugging Module')
    st.divider()
    button_cols=st.columns(4,vertical_alignment='center')
    session_btn=button_cols[0].button(
            'Session State',
            help='View session state values',
            use_container_width=True)
    show_model_btn=button_cols[1].button(
            'Show Model',
            help='View current model information',
            use_container_width=True)
    list_models_btn=button_cols[2].button(
            'List Models',
            help='View available models',
            use_container_width=True)
    running_btn=button_cols[3].button(
            'Running Models',
            help='View running models',
            use_container_width=True)
    if session_btn: ShowSessionState()
    if show_model_btn: ShowModel()
    if list_models_btn: ListModels()
    if running_btn: ShowRunningModels()

def ShowSessionState():
    st.write('### Show Session State')
    for k in st.session_state.keys():
        with st.expander(
                    label='st.session_state['+k+']',
                    expanded=True,
                    icon=':material/stylus:'):
            st.write(st.session_state[k])

def ShowModel():
    st.write('### Show Current Model')
    model_info=ollama.show(st.session_state['model'])
    st.write(model_info)

def ListModels():
    st.write('### List Available Models')
    model_list=ollama.list()
    st.write(model_list)

def ShowRunningModels():
    st.write('### Show Running Models')
    running_list=ollama.ps()
    st.write(running_list)

def ResetModule():
    """ This does the same as a browser refresh
    """
    st.divider()
    st.write('## Reset Module')
    for k in st.session_state.keys():
        if k != 'log':
            del st.session_state[k]
    st.write('Application State Was Reset :material/reset_settings:')

def DemonstrationModule():
    """ Demo and test Streamlit components
    """
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

def InitializeLogging():
    """ My typical Python logging utility adapted for Streamlit
    """
    log=st.session_state['log']
    log.setLevel(logging.NOTSET)
    logformat=logging.Formatter(
            '%(asctime)s: %(levelname)8s: %(levelno)2s: %(message)s')
    # Set file logging
    fh=logging.FileHandler('Chatbot.log')
    fh.setLevel(logging.INFO)
    fh.setFormatter(logformat)
    log.addHandler(fh)
    # Set console logging
    ch=logging.StreamHandler()
    ch.setLevel(logging.INFO) # Display only INFO or higher to console
    ch.setFormatter(logformat)
    log.addHandler(ch)
    log.debug('Script = '+__file__) # or sys.argv[0]
    log.debug('Working directory = '+os.path.dirname(__file__)) #or os.getcwd()

if __name__=='__main__':
    # See https://docs.streamlit.io/develop/api-reference/configuration/st.set_page_config
    # Choose page icon from one of the following:
    #  https://share.streamlit.io/streamlit/emoji-shortcodes
    #  https://fonts.google.com/icons?icon.set=Material+Symbols&icon.style=Rounded 
    st.set_page_config(
            page_title='Chatbot',
            page_icon=':material/smart_toy:',
            layout='wide',
            initial_sidebar_state='expanded',
            menu_items={
                    'Get Help': None,
                    'Report a bug': None,
                    'About': '# Ollama Chatbot' 
                    } )
    # set up logging to a log file and the console
    if 'log' not in st.session_state:
        st.session_state['log']=logging.getLogger()
        InitializeLogging()
    st.header('Ollama Chatbot')
    # Get a list of available ollama models
    model_dictionary=ollama.list()
    model_list=list()
    for m in model_dictionary['models']:
        model_list.append(m['model'])
    # Allow user to select a model
    # This default to the first model
    # Ollama sorts the list by the most recently added or edited
    model=st.sidebar.selectbox(
            'Select model',
            model_list,
            key='model')
    # Provide a list of modules to run
    module_list=(
            'Chatbot',
            'Demonstration',
            'Debugging',
            'Reset')
    module=st.sidebar.selectbox(
            'Select a module',
            module_list,
            key='module')
    # Run the selected module
    match module:
        case 'Chatbot': ChatbotModule()
        case 'Demonstration': DemonstrationModule()
        case 'Debugging': DebuggingModule()
        case 'Reset': ResetModule()
        case _: st.write(':construction_worker: Something is broken.')

# vim: set expandtab tabstop=4 shiftwidth=4 autoindent:
