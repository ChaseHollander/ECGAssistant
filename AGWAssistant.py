import streamlit as st 
import time
from openai import OpenAI

# Set your OpenAI API key and assistant ID here
api_key = st.secrets["apikey"]
assistant_id = st.secrets["assistantID"]

# Set OpenAI client, assistant AI, and assistant AI thread
def load_openai_client_and_assistant():
    """
    Initialize OpenAI client and assistant.

    Returns:
        client (OpenAI): OpenAI client.
        my_assistant (OpenAI.Assistant): Assistant AI.
        thread (OpenAI.Thread): Assistant AI thread.
    """
    client = OpenAI(api_key=api_key)
    my_assistant = client.beta.assistants.retrieve(assistant_id)
    thread = client.beta.threads.create()
    return client, my_assistant, thread

client,  my_assistant, assistant_thread = load_openai_client_and_assistant()

# Check in loop if assistant AI parses our request
def wait_on_run(run, thread):
    """
    Wait for assistant AI to process the request.

    Args:
        run (OpenAI.Run): Assistant AI run.
        thread (OpenAI.Thread): Assistant AI thread.

    Returns:
        run (OpenAI.Run): Updated assistant AI run.
    """
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run

# Initiate assistant AI response
def get_assistant_response(user_input=""):
    """
    Get response from assistant AI.

    Args:
        user_input (str): User input.

    Returns:
        str: Assistant AI response.
    """
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

# Function to load chat history from local storage
def load_chat_history():
    """
    Load chat history from local storage.

    Returns:
        list: Chat history.
    """
    chat_history = st.session_state.get("chat_history", [])
    return chat_history

# Function to save chat history to local storage
def save_chat_history(chat_history):
    """
    Save chat history to local storage.

    Args:
        chat_history (list): Chat history.
    """
    st.session_state.chat_history = chat_history

# Function to append new message to chat history
def append_to_chat_history(user_input, assistant_response):
    """
    Append new message to chat history.

    Args:
        user_input (str): User input.
        assistant_response (str): Assistant AI response.
    """
    chat_history = load_chat_history()
    chat_history.append({"user_input": user_input, "assistant_response": assistant_response})
    save_chat_history(chat_history)

# Function to display user message
def display_user_message(message):
    """
    Display user message.

    Args:
        message (str): User message.
    """
    st.write(f"You: {message}")

# Function to display assistant message
def display_assistant_message(message):
    """
    Display assistant message.

    Args:
        message (str): Assistant message.
    """
    st.write(f"Assistant: {message}")

# Streamlit app layout
st.title("ECG Assistant")

# Display chat history
chat_history = load_chat_history()
if len(chat_history) > 0:
    for chat in chat_history:
        if chat["user_input"]:
            display_user_message(chat["user_input"])
        if chat["assistant_response"]:
            display_assistant_message(chat["assistant_response"])

# Get user input and send message to assistant AI
user_input = st.text_input("Type a message...", "", key="user_input")
if st.button("Send") or (user_input and st.session_state.user_input == user_input):
    if user_input:
        # Perform actions using user input
        assistant_response = get_assistant_response(user_input)
        append_to_chat_history(user_input, assistant_response)
        display_user_message(user_input)
        display_assistant_message(assistant_response)
        st.session_state.user_input = ""  # Clear user input after sending
    else:
        st.warning("Please type a message before sending.")

# Add a spacer to push content to the bottom center
st.sidebar.text(" ")
