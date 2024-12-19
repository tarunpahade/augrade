import streamlit as st
import requests
import json

# Ollama API endpoint
OLLAMA_URL = "http://localhost:11434/api/generate"

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Hello! How can I help you today?"}]

def query_ollama(prompt):
    try:
        payload = {"model": "mistral", "prompt": prompt, "stream": True}
        response = requests.post(OLLAMA_URL, json=payload, headers={"Content-Type": "application/json"}, stream=True)
        
        if response.status_code == 200:
            # Initialize an empty string to store the complete response
            full_response = ""
            placeholder = st.empty()
            
            # Process the streaming response
            for line in response.iter_lines():
                if line:
                    json_response = json.loads(line)
                    response_text = json_response.get("response", "")
                    full_response += response_text
                    # Update the placeholder with the accumulated response
                    placeholder.markdown(full_response + "▌")
                    
                    # Check if this is the last message in the stream
                    if json_response.get("done", False):
                        # Remove the cursor and display final response
                        placeholder.markdown(full_response)
                        return full_response
                        
        else:
            error_msg = f"Error: {response.status_code} - {response.text}"
            st.error(error_msg)
            return error_msg
            
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        st.error(error_msg)
        return error_msg

# Streamlit UI
st.title("Chat with Ollama Mistral")
st.write("A simple chat interface for interacting with the Mistral model.")

# Display chat history using st.chat_message
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input box for user messages
if prompt := st.chat_input("Your message:"):
    # Add user's message to chat history
    st.session_state["messages"].append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Display assistant response
    with st.chat_message("assistant"):
        response = query_ollama(prompt)
        
    # Add assistant's response to chat history
    st.session_state["messages"].append({"role": "assistant", "content": response})