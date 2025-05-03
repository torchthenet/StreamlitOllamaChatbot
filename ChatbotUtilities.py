# -*- coding: utf-8 -*-
""" Common utilities for the chatbot. """

import os
import logging
import streamlit as st
import ollama
import time
import json

# Enable persistent values
# https://docs.streamlit.io/develop/concepts/architecture/widget-behavior#widgets-do-not-persist-when-not-continually-rendered
def load_key(key):
    if key in st.session_state.keys():
        st.session_state['_'+key]=st.session_state[key]
def update_key(key):
    st.session_state[key]=st.session_state['_'+key]

def StreamData(stream,metrics,temperature_key,context_key,system_key):
    """ The Ollama generator is not compatible with st.write_stream.
    This wrapper is compatible.
    The final response returns the metrics, which are saved in a dictionary.
    """
    for chunk in stream:
        if chunk['done']:
            st.session_state[metrics]=chunk.copy()
            st.session_state[metrics]['temperature']=st.session_state[temperature_key]
            st.session_state[metrics]['num_ctx']=st.session_state[context_key]
            model=st.session_state[metrics]['model']
            st.session_state[metrics]['parameter_size']=st.session_state['sys_models'][model]['parameter_size']
            st.session_state[metrics]['quantization_level']=st.session_state['sys_models'][model]['quantization_level']
            st.session_state[metrics]['context_length']=st.session_state['sys_models'][model]['context_length']
            st.session_state[metrics]['embedding_length']=st.session_state['sys_models'][model]['embedding_length']
            st.session_state[metrics]['system_prompt']=st.session_state[system_key]
        else:
            yield chunk['message']['content']

def DisplayMetrics(metrics):
    """ Display formatted Ollama metrics and message data to the user.
    """
    metrics_string='Model: '+metrics['model']
    metrics_string+='\nParameter size = '+str(metrics['parameter_size'])
    metrics_string+='\nQuantization level = '+str(metrics['quantization_level'])
    metrics_string+='\nContext tokens used = '+str(metrics['prompt_eval_count'])
    metrics_string+='\nContext token limit = '+str(metrics['num_ctx'])
    metrics_string+='\nMax context tokens = '+str(metrics['context_length'])
    metrics_string+='\nResponse tokens = '+str(metrics['eval_count'])
    metrics_string+='\nMax response tokens = '+str(metrics['embedding_length'])
    metrics_string+='\nTemperature = '+str(metrics['temperature'])
    milliseconds=metrics['total_duration']/1000000
    seconds=round(milliseconds/1000,2)
    metrics_string+='\nDuration (seconds) = '+str(seconds)
    metrics_string+='\nSystem prompt = '+metrics['system_prompt']
    with st.expander(
                label='Response Metrics',
                expanded=False,
                icon=':material/stylus:'):
        if st.session_state['clipboard_mode']:
            st.code(metrics_string, language=None, wrap_lines=True)
        else:
            st.text(metrics_string)

def SetSystemMessage(system_key,model_key):
    """ By convention (and maybe necessity) the system message is the first
    message in the conversation, and there is only one of them. If the user
    deletes the system message then delete the first message. If the use edits
    or keeps the default system message, then store that as the first message.
    The chatbot system message persists in system_key.
    """
    if system_key not in st.session_state:
        today=time.strftime('%A, %B %d, %Y')
        st.session_state[system_key]=f'Today is {today}. '
        try:
            st.session_state[system_key]+=st.session_state['sys_models'][st.session_state[model_key]]['system_prompt']
        except KeyError:
            pass
    load_key(system_key)
    system_message=st.text_area(
            label='Edit the system message here:',
            label_visibility='visible',
            key="_"+system_key,
            height=68,
            on_change=update_key,
            args=[system_key])

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
    Assume there is one metrics entry for each response message. No checks are made to ensure this.
    Since the user can restore a session from files they can edit, this may not be true.
    """
    if messages_key not in st.session_state:
        st.session_state[messages_key]=list()
        st.session_state[metrics_key]=list()
    CheckSystemMessage(messages_key,system_key)
    if len(st.session_state[messages_key]):
        metricsIndex=0
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
                if st.session_state['clipboard_mode']:
                    st.code(msg['content'], language='markdown', wrap_lines=True)
                else:
                    st.markdown(msg['content'])
            if msg['role']=='assistant':
                DisplayMetrics(st.session_state[metrics_key][metricsIndex])
                metricsIndex+=1
    st.divider()

def UpdateSessionLogs(session_log_key,metrics_log_key,messages_key,metrics_key):
    """ Create or update logs of the prompts, responses, and metrics in the session."""
    if session_log_key not in st.session_state:
        # Create filenames for this session log and the metrics log.
        # Create new log files if they do not exist.
        now=time.strftime('%Y-%m-%d-%H%M%S')
        cb_session_log_file=f'ChatbotSession_{now}.log'
        st.session_state[session_log_key] = cb_session_log_file
        cb_metrics_log_file=f'ChatbotSession_{now}_metrics.log'
        st.session_state[metrics_log_key] = cb_metrics_log_file
        with open(cb_session_log_file, 'w') as f:
            f.write('Chatbot Session Log\n')
        with open(cb_metrics_log_file, 'w') as f:
            f.write('Chatbot Metrics Log\n')
    # Write the current prompt and response to the session log file
    with open(st.session_state[session_log_key], 'w') as f:
        json.dump(st.session_state[messages_key], f, indent=4)
    # Write the current metrics to the metrics log file
    with open(st.session_state[metrics_log_key], 'w') as f:
        json.dump(st.session_state[metrics_key], f, indent=4)

@st.dialog('Restore a preior session')
def RestoreSessionLogs(messages_key,metrics_key):
    """ Restore the session and metrics lists from user provided log files.
    There is no check to see if the files are valid. """
    st.write('## Restore Session Logs')
    st.divider()
    st.markdown('Upload the session log file (ChatbotSession_*.log) and the metrics log file (ChatbotSession_*_metrics.log)')
    st.markdown('The session log file contains the chat history and the metrics log file contains the metrics for each response.')
    # Upload the session log file
    st.markdown('\n\nSession log file:')
    session_log_file=st.file_uploader(
            label='Upload a session log file',
            type='log',
            label_visibility='collapsed')
    # Upload the metrics log file
    st.markdown('Metrics log file:')
    metrics_log_file=st.file_uploader(
            label='Upload a metrics log file',
            type='log',
            label_visibility='collapsed')
    if session_log_file and metrics_log_file:
        # Read the session log file and restore the messages list
        st.session_state[messages_key]=json.load(session_log_file)
        # Read the metrics log file and restore the metrics list
        st.session_state[metrics_key]=json.load(metrics_log_file)
        st.write('Session restored.')
    st.write('Press :red[Close] to close this dialog.')
    if st.button('Close'):
        st.rerun()

def DebuggingModule():
    """ Provide buttons to access debug views """
    st.write('## Debugging Module')
    st.divider()
    button_cols=st.columns(4,vertical_alignment='center')
    session_btn=button_cols[0].button(
            'Session State',
            help='View session state values',
            use_container_width=True)
    show_model_btn=button_cols[1].button(
            'Show Models',
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
    """ Dump the session state """
    st.write('### Show Session State')
    for k in st.session_state.keys():
        with st.expander(
                    label='st.session_state['+k+']',
                    expanded=True,
                    icon=':material/stylus:'):
            st.write(st.session_state[k])

def ShowModel():
    """ Show current model """
    st.write('### Show Current Models')
    model_list=(
            'cb_model',
            'c2_model',
            'c3_model',
            'c4_model',
            'c5_model')
    for model in model_list:
        if model in st.session_state:
            state=st.session_state[model]
        else:
            state='Not Selected'
        with st.expander(
                    label=f'Model {model} = {state}',
                    expanded=False,
                    icon=':material/stylus:'):
            if model in st.session_state:
                model_info=ollama.show(st.session_state[model])
            else:
                model_info=f'{model} has not been selected yet.'
            st.write(model_info)

def ListModels():
    """ Show all available models """
    st.write('### List Available Models')
    model_list=ollama.list()
    st.write(model_list)
    return

def ShowRunningModels():
    """ Display models currently active in ollama """
    st.write('### Show Running Models')
    running_list=ollama.ps()
    st.write(running_list)

def ResetModule():
    """ This does the same as a browser refresh but preserves the log and sys_models. """
    st.divider()
    st.write('## Reset Module')
    for k in st.session_state.keys():
        if k == 'log':
            st.session_state['log'].info('Application reset - session_state cleared')
        elif k[:4] == 'sys_':
            pass
        else:
            del st.session_state[k]
    st.write('Application State Was Reset :material/reset_settings:')

def ResetModel(model_key,old_model_key,system_key):
    """ Reset the model to the default model. This is called when the user
    selects a different model from the sidebar.
    Deleting cb_system causes SetSystemMessage() to check if there is a model default system prompt.
    A simple delete of the system_key results in issues - can't edit/update system prompt.
    Instead need to check if the new model is different from the old model.
    """
    if "_"+model_key not in st.session_state.keys():
        return
    update_key(model_key)
    if model_key != old_model_key:
        old_model_key=model_key
        if system_key in st.session_state:
            del st.session_state[system_key]

@st.cache_data
def InventoryModels():
    """ Inventory available models. Add features/parameters to st.session_state.
    Selected details are included in every metrics summary displayed to the user.
    The max context length is used to set the slider max_value."""
    st.session_state['sys_models']=dict()
    for model in ollama.list()['models']:
        try:
            del model_vision_embedding_length
        except NameError:
            pass
        try:
            del model_system_prompt
        except NameError:
            pass
        model_name=model['model']
        model_parameter_size=model['details']['parameter_size']
        model_info=ollama.show(model['model'])
        try:
            model_system_prompt=model_info['system']
        except KeyError:
            pass
        for k in model_info.keys():
            if k == 'details':
                model_quantization_level=model_info[k]['quantization_level']
            if k == 'model_info':
                for p in model_info[k].keys():
                    # Context length is capped at 100k (102400) even though some models have larger context lengths.
                    # Vision embedding length is not currently used in the chatbot module.
                    if ".context_length" == p[-15:]:
                        model_context_length=model_info[k][p]
                        if model_context_length > 102400:
                            model_context_length=102400
                    elif "vision.embedding_length" == p[-23:]:
                        model_vision_embedding_length=model_info[k][p]
                    elif ".embedding_length" == p[-17:]:
                        model_embedding_length=model_info[k][p]
        model_dictionary={
                'name':model_name,
                'parameter_size':model_parameter_size,
                'quantization_level':model_quantization_level,
                'context_length':model_context_length,
                'embedding_length':model_embedding_length
                }
        try:
            model_dictionary['vision_embedding_length']=model_vision_embedding_length
        except NameError:
            pass
        try:
            model_dictionary['system_prompt']=model_system_prompt
        except NameError:
            pass
        st.session_state['sys_models'][model_name] = model_dictionary

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
    log.info('Script full = '+__file__) # or sys.argv[0]
    log.info('Script name = '+os.path.basename(__file__))
    log.info('Script path = '+os.path.dirname(__file__)) # or os.getcwd()
