# Original code provided by mistral-small:22b
# Fails to read back json without exceptions
import streamlit as st
from datetime import datetime
import json

# Define the filename
filename = 'task_log.txt'

def log_task(task, start_time):
    with open(filename, 'a+') as file:
        tasks=list()
        try:
            file.seek(0)
            tasks = json.load(file)
        except:
            pass
    entry = {
        'task': task,
        'start_time': start_time.isoformat()  # Use ISO format for datetime
    }
    tasks.append(entry)
    with open(filename,'w') as file:
        json.dump(tasks, file)

def read_tasks():
    with open(filename, 'r') as file:
        tasks=list()
        tasks = json.load(file)
    return tasks

# Streamlit app
st.title('Task Logger')

# Radio buttons for task selection
task_options = ['Write code for Streamlit app', 'Design UI/UX', 'Test functionality', 'Other']
selected_task = st.radio('Select Task:', task_options)

if selected_task:
    log_task(selected_task, datetime.now())
    st.success('Task logged!')

tasks = read_tasks()

for task in tasks[::-1]:
    st.write(f"Task: {task['task']}, Start Time: {task['start_time']}")