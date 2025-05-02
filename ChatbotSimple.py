# -*- coding: utf-8 -*-
"""
ChatbotSimple.py - Simple chatbot app for Ollama
The latest (hopefully working) version should always be available here:
https://github.com/torchthenet/StreamlitOllamaChatbot
"""

import streamlit as st
import ollama
import time
import json

# Enable persistent values
# https://docs.streamlit.io/develop/concepts/architecture/widget-behavior#widgets-do-not-persist-when-not-continually-rendered
def load_key(key):
    if key in st.session_state.keys():
        st.session_state["_"+key]=st.session_state[key]
def update_key(key):
    st.session_state[key]=st.session_state["_"+key]

def StreamData(stream,metrics):
    """ The Ollama generator is not compatible with st.write_stream.
    This wrapper is compatible.
    The final response returns the metrics, which are saved in a dictionary.
    """
    for chunk in stream:
        if chunk['done']:
            st.session_state[metrics]=chunk.copy()
            st.session_state[metrics]['temperature']=st.session_state['cb_temperature']
            st.session_state[metrics]['num_ctx']=st.session_state['cb_context']
            model=st.session_state[metrics]['model']
            st.session_state[metrics]['parameter_size']=st.session_state['sys_models'][model]['parameter_size']
            st.session_state[metrics]['quantization_level']=st.session_state['sys_models'][model]['quantization_level']
            st.session_state[metrics]['context_length']=st.session_state['sys_models'][model]['context_length']
            st.session_state[metrics]['embedding_length']=st.session_state['sys_models'][model]['embedding_length']
            st.session_state[metrics]['system_prompt']=st.session_state['cb_system']
        else:
            yield chunk['message']['content']

def DisplayMetrics(metrics):
    """ Display formatted Ollama metrics and message data to the user.
    """
    metrics_string='Model: '+metrics['model']
    metrics_string+='\nParameter size = '+str(metrics['parameter_size'])
    metrics_string+='\nContext tokens used = '+str(metrics['prompt_eval_count'])
    metrics_string+='\nContext token limit = '+str(metrics['num_ctx'])
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
        st.text(metrics_string)

def SetSystemMessage():
    """ By convention (and maybe necessity) the system message is the first
    message in the conversation, and there is only one of them. If the user
    deletes the system message then delete the first message. If the use edits
    or keeps the default system message, then store that as the first message.
    The chatbot system message persists in 'cb_system'.
    """
    if 'cb_system' not in st.session_state:
        today=time.strftime('%A, %B %d, %Y')
        st.session_state['cb_system']=f'Today is {today}. '
        try:
            st.session_state['cb_system']+=st.session_state['sys_models'][st.session_state['cb_model']]['system_prompt']
        except KeyError:
            pass
    load_key('cb_system')
    system_message=st.text_area(
            label='Edit the system message here:',
            label_visibility='visible',
            key="_"+'cb_system',
            height=68,
            on_change=update_key,
            args=['cb_system'])

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
    Assume there is one metrics entry for each response message. No checks are made to ensure this.
    Since the user can restore a session from files they can edit, this may not be true.
    """
    if 'cb_messages' not in st.session_state:
        st.session_state['cb_messages']=list()
        st.session_state['cb_metrics']=list()
    CheckSystemMessage()
    if len(st.session_state['cb_messages']):
        metricsIndex=0
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
                st.markdown(msg['content'])
            if msg['role']=='assistant':
                DisplayMetrics(st.session_state['cb_metrics'][metricsIndex])
                metricsIndex+=1
    st.divider()

def GenerateNextResponse():
    """ Handle prompt submission. 
    First, add the user's prompt to the messages list, then obtain and add the LLM response.
    Also, save the metrics to the chatbot metrics list.
    """
    # Append the user prompt to the messages list
    message={'role':'user',
             'content':st.session_state['cb_prompt']
            }
    st.session_state['cb_messages'].append(message)
    # Get the model response and metrics
    response_metrics='metrics'
    stream=ollama.chat(
            model=st.session_state['cb_model'],
            messages=st.session_state['cb_messages'],
            options={'temperature':st.session_state['cb_temperature'],
                     'num_ctx':st.session_state['cb_context']},
            stream=True)
    with st.expander(
                label='Response',
                expanded=True,
                icon=':material/smart_toy:'):
        response_text=st.write_stream(StreamData(stream,response_metrics))
    message={'role':'assistant',
            'content':response_text
            }
    st.session_state['cb_messages'].append(message)
    st.session_state['cb_metrics'].append(st.session_state[response_metrics])
    # Clear the prompt after it is successfully submitted
    st.session_state['cb_prompt']=str()
    # Save the session and metrics logs
    UpdateSessionLogs()
    st.rerun()

def UpdateSessionLogs():
    """ Create or update logs of the prompts, responses, and metrics in the session."""
    if 'cb_session_log_file' not in st.session_state:
        # Create new log files if they do not exist.
        now=time.strftime('%Y-%m-%d-%H%M%S')
        cb_session_log_file=f'ChatbotSession_{now}.log'
        st.session_state['cb_session_log_file'] = cb_session_log_file
        cb_metrics_log_file=f'ChatbotSession_{now}_metrics.log'
        st.session_state['cb_metrics_log_file'] = cb_metrics_log_file
        with open(cb_session_log_file, 'w') as f:
            f.write('Chatbot Session Log\n')
        with open(cb_metrics_log_file, 'w') as f:
            f.write('Chatbot Metrics Log\n')
    # Write the current prompt and response to the session log file
    with open(st.session_state['cb_session_log_file'], 'w') as f:
        json.dump(st.session_state['cb_messages'], f, indent=4)
    # Write the current metrics to the metrics log file
    with open(st.session_state['cb_metrics_log_file'], 'w') as f:
        json.dump(st.session_state['cb_metrics'], f, indent=4)

def RestoreSessionLogs():
    """ Restore the session and metrics lists from user provided log files.
    There is no check to see if the files are valid. """
    st.markdown('### Restore Session Logs')
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
        st.session_state['cb_messages']=json.load(session_log_file)
        # Read the metrics log file and restore the metrics list
        st.session_state['cb_metrics']=json.load(metrics_log_file)
        st.write('Session restored.')

def ChatbotModule():
    """ Manage a chatbot conversation instance.
    Display the message history and provide text input and buttons.
    """
    # Get a list of available ollama models for the selectbox
    model_list=list()
    for m in st.session_state['sys_models'].keys():
        model_list.append(m)
    # Allow user to select a model
    # This defaults to the first model
    # Ollama sorts the list by the most recently added or edited
    load_key('cb_model')
    model=st.selectbox(
            'Select model',
            model_list,
            key="_"+'cb_model',
            on_change=ResetModel)
    if 'cb_model' not in st.session_state.keys():
        st.session_state['cb_model']=model
    if 'cb_model_old' not in st.session_state.keys():
        st.session_state['cb_model_old']=model
    SetSystemMessage()
    # Display the chat history if it exists
    DisplayChatHistory()
    # The st.chat_input always displays at the bottom of the screen.
    # Pressing return submits the prompt.
    if chatbot_prompt:=st.chat_input():
        st.session_state['cb_prompt']=chatbot_prompt
        GenerateNextResponse()
    # Create 3 button areas
    button_cols=st.columns((1,1,2),vertical_alignment='center')
    # New Chat button
    new_chat_btn=button_cols[0].button(
            'New Chat',
            help='Start a new chat',
            use_container_width=True)
    if new_chat_btn:
        if 'cb_system' in st.session_state.keys():
            del st.session_state['cb_system']
        if 'cb_messages' in st.session_state.keys():
            del st.session_state['cb_messages']
        if 'cb_metrics' in st.session_state.keys():
            del st.session_state['cb_metrics']
        if 'cb_session_log_file' in st.session_state.keys():
            del st.session_state['cb_session_log_file']
        if 'cb_metrics_log_file' in st.session_state.keys():
            del st.session_state['cb_metrics_log_file']
        if 'cb_prompt' in st.session_state.keys():
            del st.session_state['cb_prompt']
        st.rerun()
    # Temperature Slider
    button_cols[1].slider(
            label='Temperature',
            help='Adjust the randomness of the responses',
            value=0.1,
            min_value=0.0,
            max_value=1.0,
            step=0.1,
            key='cb_temperature')
    # Context Size Slider
    model=st.session_state['cb_model']
    max_context_size=st.session_state['sys_models'][model]['context_length']
    button_cols[2].slider(
            label='Context token limit',
            help='Adjust the number of context tokens',
            value=2048,
            min_value=1024,
            max_value=max_context_size,
            step=1024,
            key='cb_context')

def DebuggingModule():
    """ Provide buttons to access debug views """
    st.markdown('### Debugging Module')
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
    st.write('### Show Current Model')
    st.write('Model: '+st.session_state['cb_model'])
    model_info=ollama.show(st.session_state['cb_model'])
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

def ResetModel():
    """ Reset the model to the default model. This is called when the user selects a different model from the sidebar.
    Deleting cb_system causes SetSystemMessage() to check if there is a model default system prompt.
    A simple delete of the 'cb_system' results in issues - can't edit/update system prompt.
    Instead need to check if the new model is different from the old model.
    """
    if "_"+'cb_model' not in st.session_state.keys():
        return
    update_key('cb_model')
    if st.session_state['cb_model'] != st.session_state['cb_model_old']:
        st.session_state['cb_model_old']=st.session_state['cb_model']
        if 'cb_system' in st.session_state.keys():
            del st.session_state['cb_system']

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

if __name__=='__main__':
    # The Chatbot application.
    st.set_page_config(
            page_title='Chatbot',
            page_icon=':material/smart_toy:',
            layout='wide',
            initial_sidebar_state='expanded',
            menu_items={
                    'Get Help': None,
                    'Report a bug': None,
                    'About': '# Simple Chatbot for Ollama'
                    } )
    # Inventory available Ollama models, adding features/parameters to st.session_state
    InventoryModels()
    st.markdown('## Simple Chatbot for Ollama')
    # Provide a list of modules to run
    module_list=(
            'Chatbot',
            'Restore',
            'Debugging',
            'Reset')
    module=st.selectbox(
            'Select a module',
            module_list,
            key='module')
    # Run the selected module
    match module:
        case 'Chatbot': ChatbotModule()
        case 'Restore': RestoreSessionLogs()
        case 'Debugging': DebuggingModule()
        case 'Reset': ResetModule()
        case _: st.write(':construction_worker: Something is broken.')

# vim: set expandtab tabstop=4 shiftwidth=4 autoindent: