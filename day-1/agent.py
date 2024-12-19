import streamlit as st
import requests
import json
import sys
from io import StringIO

# Ollama API endpoint
OLLAMA_URL = "http://localhost:11434/api/generate"

# Set page title and configuration
st.set_page_config(page_title="Code Assistant", layout="wide")
st.title("Code Assistant with Mistral")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Hello! I can help you write and execute Python code. What would you like to do?"}]

def execute_code(code):
    """Execute the Python code and return its output"""
    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()
    
    try:
        exec(code)
        sys.stdout = old_stdout
        return redirected_output.getvalue()
    except Exception as e:
        sys.stdout = old_stdout
        return f"Error: {str(e)}"

def query_ollama(prompt):
    try:
        payload = {
            "model": "mistral",
            "prompt": f"You are a Python coding assistant. Please provide only executable Python code for this request: {prompt}",
            "stream": True
        }
        response = requests.post(OLLAMA_URL, json=payload, headers={"Content-Type": "application/json"}, stream=True)
        
        if response.status_code == 200:
            full_response = ""
            placeholder = st.empty()
            
            for line in response.iter_lines():
                if line:
                    json_response = json.loads(line)
                    response_text = json_response.get("response", "")
                    full_response += response_text
                    placeholder.markdown(full_response + "▌")
                    
                    if json_response.get("done", False):
                        placeholder.markdown(full_response)
                        return full_response
        else:
            error_msg = f"Error: {response.status_code} - {response.text}"
            st.error(error_msg)
            return error_msg
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return str(e)

# Chat interface
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("What code would you like me to write?"):
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant"):
        response = query_ollama(prompt)
        
        # Extract code blocks from the response
        code_blocks = []
        if "```python" in response:
            code_blocks = response.split("```python")[1:]
            code_blocks = [block.split("```")[0].strip() for block in code_blocks]
        elif "```" in response:
            code_blocks = response.split("```")[1::2]
        
        if code_blocks:
            for code in code_blocks:
                st.code(code, language="python")
                st.write("Output:")
                with st.spinner("Executing code..."):
                    output = execute_code(code)
                    st.write(output)
        else:
            st.write(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})

# Add sidebar with instructions
with st.sidebar:
    st.markdown("""
    ### Instructions
    1. Type your coding request in the chat
    2. The assistant will generate the code
    3. The code will be automatically executed
    4. You'll see both the code and its output
    
    ### Examples
    - "Write a function to calculate fibonacci series"
    - "Create a simple calculator"
    - "Generate a random password"
    """)