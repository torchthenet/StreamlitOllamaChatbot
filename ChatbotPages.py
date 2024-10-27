# -*- coding: utf-8 -*-
"""
ChatbotPages.py - Chatbot app for Ollama
Expanded Chatbot.py to hold multiple conversations at once.
Each conversation is on a different page, potentially with a different model.
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

# Enable persistent values
# docs.streamlit.io/develop/concepts/architecture/widget-behavior#widgets-do-not-persist-when-not-continually-rendered
def store_value(key):
    st.session_state[key] = st.session_state["_"+key]
def load_value(key):
    if key in st.session_state.keys():
        st.session_state["_"+key] = st.session_state[key]

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

def SetSystemMessage(system_key):
    """ By convention (and maybe necessity) the system message is the first
    message in the conversation, and there is only one of them. If the user
    deletes the system message then delete the first message. If the use edits
    or keeps the default system message, then store that as the first message.
    The chatbot system message persists in the cb_system key.
    """
    if system_key not in st.session_state:
        today=time.strftime('%A, %B %d, %Y')
        st.session_state[system_key]=f'Today is {today}.'
    system_message=st.text_area(
            label='System message',
            label_visibility='visible',
            key=system_key,
            height=100)

def CheckSystemMessage(messages_key,system_key):
    """ Manage the system message. If this module has just started then
    add the system message to the messages list. If the user edits the system
    message then update it. If the user deletes the content then remove it.
    """
    # If the system message is blank then delete the system message
    if len(st.session_state[system_key])==0:
        if len(st.session_state[messages_key])>0:
            if st.session_state[messages_key][0]['role']=='system':
                del st.session_state[messages_key][0]
    else:
        # create the system message
        message={'role':'system',
                 'content':st.session_state[system_key]
                }
        if st.session_state[messages_key]:
            # if there are messages then the system message is placed first
            if st.session_state[messages_key][0]['role']=='system':
                # easier to just replace the message than check if it changed
                st.session_state[messages_key][0]=message
            else:
                st.session_state[messages_key].insert(0,message)
        else:
            # if there are no message then append the system message
            st.session_state[messages_key].append(message)

def DisplayChatHistory(messages_key,system_key,metrics_key):
    """ Display the chat history if there is one. Each message is placed in a
    box with an icon and role name. Every response message is followed by the
    metrics from that query and response.
    If this module has just launched then create empty lists to fill in later.
    """
    if messages_key not in st.session_state:
        st.session_state[messages_key]=list()
        st.session_state[metrics_key]=list()
    CheckSystemMessage(messages_key,system_key)
    if len(st.session_state[messages_key]):
        j=0
        for msg in st.session_state[messages_key]:
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
                DisplayMetrics(st.session_state[metrics_key][j])
                j+=1
    st.divider()

def GenerateNextResponse(messages_key,metrics_key,prompt_key,temperature_key,model_key):
    """ Handle the generate response button. First, add the user's prompt
    to the messages list, then obtain and add the LLM response. Also, save
    the metrics to the chatbot metrics list.
    The LLM query includes the current temperature.
    Call st.rerun to force display of the user prompt in a non-editable way.
    """
    message={'role':'user',
             'content':st.session_state[prompt_key]
            }
    st.session_state[messages_key].append(message)
    stream=ollama.chat(
            model=st.session_state[model_key],
            messages=st.session_state[messages_key],
            options={'temperature':st.session_state[temperature_key]},
            stream=True)
    with st.expander(
                label='Response',
                expanded=True,
                icon=':material/smart_toy:'):
        response_text=st.write_stream(StreamData(stream))
    message={'role':'assistant',
            'content':response_text
            }
    st.session_state[messages_key].append(message)
    st.session_state[metrics_key].append(st.session_state['metrics'])
    st.rerun()

def ChatbotModule(messages_key,metrics_key,system_key,prompt_key,temperature_key,model_key):
    SetSystemMessage(system_key)
    # Display the chat history if it exists
    DisplayChatHistory(messages_key,system_key,metrics_key)
    # Provide an editable text box for the next prompt
    if prompt_key not in st.session_state:
        st.session_state[prompt_key]='Enter your prompt here'
    with st.expander(
                label="Question",
                expanded=True,
                icon=':material/person:'):
        chatbot_prompt=st.text_area(
                label='Question',
                label_visibility='collapsed',
                value=st.session_state[prompt_key],
                height=100)
    st.session_state[prompt_key]=chatbot_prompt
    button_cols=st.columns(4,vertical_alignment='bottom')
    new_chat_btn=button_cols[0].button(
            'New Chat',
            help='Start a new chat',
            use_container_width=True)
    # Get a list of available ollama models
    model_dictionary=ollama.list()
    model_list=list()
    for m in model_dictionary['models']:
        model_list.append(m['name'])
    st.session_state[model_key]=button_cols[1].selectbox(
            'Select model',
            model_list,
            key='_'+model_key)
    button_cols[2].slider(
            label='Temperature',
            value=0.1,
            min_value=0.0,
            max_value=1.0,
            step=0.1,
            key=temperature_key)
    generate_btn=button_cols[3].button(
            'Submit',
            help='Submit prompt to large language model',
            use_container_width=True)
    if new_chat_btn:
        del st.session_state[system_key]
        del st.session_state[messages_key]
        del st.session_state[metrics_key]
        st.rerun()
    if generate_btn:
        GenerateNextResponse(messages_key,metrics_key,prompt_key,
                             temperature_key,model_key)

def chat_one():
    messages_key='c1_messages'
    metrics_key='c1_metrics_list'
    system_key='c1_system'
    prompt_key='c1_prompt'
    temperature_key='c1_temperature'
    model_key='c1_model'
    ChatbotModule(messages_key,metrics_key,system_key,prompt_key,
                  temperature_key,model_key)

def chat_two():
    messages_key='c2_messages'
    metrics_key='c2_metrics_list'
    system_key='c2_system'
    prompt_key='c2_prompt'
    temperature_key='c2_temperature'
    model_key='c2_model'
    ChatbotModule(messages_key,metrics_key,system_key,prompt_key,
                  temperature_key,model_key)

def chat_three():
    messages_key='c3_messages'
    metrics_key='c3_metrics_list'
    system_key='c3_system'
    prompt_key='c3_prompt'
    temperature_key='c3_temperature'
    model_key='c3_model'
    ChatbotModule(messages_key,metrics_key,system_key,prompt_key,
                  temperature_key,model_key)

def chat_four():
    messages_key='c4_messages'
    metrics_key='c4_metrics_list'
    system_key='c4_system'
    prompt_key='c4_prompt'
    temperature_key='c4_temperature'
    model_key='c4_model'
    ChatbotModule(messages_key,metrics_key,system_key,prompt_key,
                  temperature_key,model_key)

def chat_five():
    messages_key='c5_messages'
    metrics_key='c5_metrics_list'
    system_key='c5_system'
    prompt_key='c5_prompt'
    temperature_key='c5_temperature'
    model_key='c5_model'
    ChatbotModule(messages_key,metrics_key,system_key,prompt_key,
                  temperature_key,model_key)

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
                    expanded=False,
                    icon=':material/stylus:'):
            st.write(st.session_state[k])

def ShowModel():
    st.write('### Show Current Model')
    model_list=(
            'c1_model',
            'c2_model',
            'c3_model',
            'c4_model',
            'c5_model')
    model=st.selectbox(
            'Select a model',
            model_list,
            key='model')
    if model in st.session_state:
        model_info=ollama.show(st.session_state[model])
    else:
        model_info=f'{model} has not been selected yet.'
    st.write(f'Model = {st.session_state[model]}')
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
    For ChatbotPages, this does not delete 'log'.
    """
    st.divider()
    st.write('## Reset Module')
    for k in st.session_state.keys():
        if k!='log':
            del st.session_state[k]
        else:
            st.session_state['log'].info('Application reset - session_state cleared')
    st.write('Application State Was Reset :material/reset_settings:')

def InitializeLogging():
    """ My typical Python logging utility adapted for Streamlit
    """
    log=st.session_state['log']
    log.setLevel(logging.NOTSET)
    logformat=logging.Formatter(
            '%(asctime)s: %(levelname)8s: %(levelno)2s: %(message)s')
    # Set file logging
    fh=logging.FileHandler('ChatbotPages.log')
    fh.setLevel(logging.INFO)
    fh.setFormatter(logformat)
    log.addHandler(fh)
    # Set console logging
    ch=logging.StreamHandler()
    ch.setLevel(logging.INFO) # Display only INFO or higher to console
    ch.setFormatter(logformat)
    log.addHandler(ch)
    log.info('Script = '+__file__) # or sys.argv[0]
    log.info('Working directory = '+os.path.dirname(__file__)) #or os.getcwd()

if __name__=='__main__':
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
                    'About': '# Ollama Chatbot' 
                    } )
    # set up logging to a log file and the console
    if 'log' not in st.session_state:
        st.session_state['log']=logging.getLogger()
        InitializeLogging()
    st.sidebar.header('Ollama Chatbot')
    # Provide a list of pages to view
    # can't use shortcodes so copy and paste the images from
    # https://share.streamlit.io/streamlit/emoji-shortcodes
    # 1 = ":one:", 2 = ":two:", ...
    # debug = ":beetle:", reset = ":sparkles:"
    pages = {
        "Conversations": [
            st.Page(chat_one, title='Chat One',icon='1️⃣'),
            st.Page(chat_two, title='Chat Two',icon='2️⃣'),
            st.Page(chat_three, title='Chat Three',icon='3️⃣'),
            st.Page(chat_four, title='Chat Four',icon='4️⃣'),
            st.Page(chat_five, title='Chat Five',icon='5️⃣'),
        ],
        "Debugging": [
            st.Page(DebuggingModule, title='Debug',icon='🪲'),
            st.Page(ResetModule, title='Reset',icon='✨'),
        ],
    }
    pg = st.navigation(pages)
    pg.run()

# vim: set expandtab tabstop=4 shiftwidth=4 autoindent: