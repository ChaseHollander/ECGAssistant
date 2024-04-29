import streamlit as st 
import time
from openai import OpenAI 

# Set your OpenAI API key and assistant ID here
api_key = st.secrets["apikey"]
assistant_id = st.secrets["assistantID"]

# Set OpenAI client, assistant AI, and assistant AI thread
def load_openai_client_and_assistant():
    client = OpenAI(api_key=api_key)
    my_assistant = client.beta.assistants.retrieve(assistant_id)
    thread = client.beta.threads.create()
    return client, my_assistant, thread

client,  my_assistant, assistant_thread = load_openai_client_and_assistant()

# Check in loop if assistant AI parses our request
def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run

# Initiate assistant AI response
def get_assistant_response(user_input=""):
    message = client.beta.threads.messages.create(
        thread_id=assistant_thread.id,
        role="user",
        content=user_input,
    )

    run = client.beta.threads.runs.create(
        thread_id=assistant_thread.id,
        assistant_id=assistant_id,
    )

    run = wait_on_run(run, assistant_thread)

    # Retrieve all the messages added after our last user message
    messages = client.beta.threads.messages.list(
        thread_id=assistant_thread.id, order="asc", after=message.id
    )

    return messages.data[0].content[0].text.value

# Streamlit app layout
st.title("ECG Assistant")

# User input
user_input = st.text_input("Ask a Question:")

# Display user input
st.write("You entered:", user_input)

# If user input is not empty, get assistant's response and display it
if user_input:
    result = get_assistant_response(user_input)
    st.header('Assistant:')
    st.text(result)
