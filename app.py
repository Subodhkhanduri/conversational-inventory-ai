import streamlit as st
import requests
import time
import json
import base64 # Import base64

# --- Configuration ---
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
                st.error(f"Connection error: Could not connect to the backend at {BACKEND_URL}.")


# --- Main Chat Interface ---
if not st.session_state.session_id:
    st.info("Please upload a CSV file in the sidebar to begin.")
else:
    # --- MODIFIED: Display chat messages from history (now includes images) ---
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            # Check if there's an image and display it
            if message.get("image"):
                st.image(base64.b64decode(message["image"]), caption="Forecast Visualization")

    # Accept user input
    if prompt := st.chat_input("Ask a question about your inventory..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # --- MODIFIED: Streaming logic to handle text and images ---
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            chart_b64 = None  # Variable to hold our chart
            
            try:
                payload = {
                    "session_id": st.session_state.session_id,
                    "messages": st.session_state.messages
                }
                
                with requests.post(f"{BACKEND_URL}/ask", json=payload, stream=True) as r:
                    r.raise_for_status()
                    for chunk in r.iter_content(chunk_size=None, decode_unicode=True):
                        # Check if the chunk is our JSON data
                        if chunk.startswith('{"chart_b64":'):
                            try:
                                chart_data = json.loads(chunk)
                                chart_b64 = chart_data.get("chart_b64")
                            except json.JSONDecodeError:
                                # Not valid JSON, treat it as text
                                full_response += chunk
                        else:
                            full_response += chunk
                        
                        # Update text as it streams
                        message_placeholder.markdown(full_response + "▌")
                
                # Display final text
                message_placeholder.markdown(full_response)
                
                # If we received a chart, display it
                if chart_b64:
                    st.image(base64.b64decode(chart_b64), caption="Forecast Visualization")
            
            except requests.exceptions.RequestException as e:
                full_response = f"Error communicating with backend: {e}"
                message_placeholder.error(full_response)

            # --- MODIFIED: Add assistant response (and image!) to chat history ---
            st.session_state.messages.append({"role": "assistant", "content": full_response, "image": chart_b64})
