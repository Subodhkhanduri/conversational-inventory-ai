import streamlit as st
import requests
import time

# --- Configuration ---
# app.py
BACKEND_URL = "http://127.0.0.1:8000/api/v1"

# --- UI Setup ---
st.set_page_config(page_title="Inventory AI Assistant", layout="wide")
st.title("🤖 Inventory Management AI Assistant")
st.caption("Upload your inventory CSV and ask questions in natural language.")

# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = None

# --- Sidebar for File Upload ---
with st.sidebar:
    st.header("Upload Your Data")
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None:
        with st.spinner('Processing file...'):
            try:
                files = {'file': (uploaded_file.name, uploaded_file.getvalue(), 'text/csv')}
                response = requests.post(f"{BACKEND_URL}/upload", files=files)
                
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.session_id = data.get("session_id")
                    st.success(f"File '{uploaded_file.name}' uploaded successfully!")
                    st.info(f"Columns found: {', '.join(data.get('columns', []))}")
                    # Clear chat history on new file upload
                    st.session_state.messages = []
                else:
                    st.error(f"Error: {response.status_code} - {response.text}")
            except requests.exceptions.RequestException as e:
                st.error(f"Connection error: Could not connect to the backend at {BACKEND_URL}. Please ensure the backend is running.")


# --- Main Chat Interface ---
if not st.session_state.session_id:
    st.info("Please upload a CSV file in the sidebar to begin.")
else:
    # Display chat messages from history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("Ask a question about your inventory..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            try:
                # Prepare data for the backend
                data = {"session_id": st.session_state.session_id, "query": prompt}
                
                # Stream response from the backend
                with requests.post(f"{BACKEND_URL}/ask", data=data, stream=True) as r:
                    r.raise_for_status() # Raise an exception for bad status codes
                    for chunk in r.iter_content(chunk_size=None, decode_unicode=True):
                        full_response += chunk
                        # Add a slight delay to make streaming visible
                        time.sleep(0.01)
                        message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
            except requests.exceptions.RequestException as e:
                full_response = f"Error communicating with backend: {e}"
                message_placeholder.error(full_response)

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})