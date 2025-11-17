import streamlit as st
import requests
import uuid
import base64

# --------------------------
# BACKEND URL
# --------------------------
BACKEND_URL = "http://127.0.0.1:8000/api/v1"

# --------------------------
# PAGE CONFIG
# --------------------------
st.set_page_config(page_title="Inventory AI Assistant", layout="wide")
st.title("🤖 Inventory Management AI Assistant")
st.caption("Upload your inventory CSV and ask questions in natural language.")

# --------------------------
# SESSION STATE
# --------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

session_id = st.session_state.session_id


# ================================
# SIDEBAR — FILE UPLOAD
# ================================
with st.sidebar:

    st.header("Upload Your Data")
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None:
        with st.spinner("Uploading and processing file..."):

            try:
                response = requests.post(
                    f"{BACKEND_URL}/upload",
                    data={"session_id": session_id},
                    files={"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")},
                )

                if response.status_code == 200:
                    info = response.json()

                    st.success("File uploaded successfully!")
                    st.info("Columns: " + ", ".join(info["columns"]))

                    # Reset chat history for new dataset
                    st.session_state.messages = []

                else:
                    st.error(f"Upload Error {response.status_code}: {response.text}")

            except Exception as e:
                st.error(f"❌ Backend connection error: {e}")


# ================================
# MAIN CHAT INTERFACE
# ================================
if uploaded_file is None:
    st.info("Please upload a CSV file in the sidebar to begin.")
else:

    # Render previous messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg.get("image"):
                st.image(base64.b64decode(msg["image"]), caption="Visualization")


    # ========= USER INPUT =========
    if prompt := st.chat_input("Ask a question about your inventory…"):

        # Display user message
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.write(prompt)

        # Placeholder for assistant
        with st.chat_message("assistant"):
            placeholder = st.empty()
            placeholder.write("Thinking...")

            try:
                # ---------- SEND TO BACKEND ----------
                response = requests.post(
                    f"{BACKEND_URL}/ask",
                    data={"query": prompt, "session_id": session_id},
                )

                if response.status_code != 200:
                    placeholder.error(f"❌ Error {response.status_code}: {response.text}")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"Error: {response.text}"
                    })
                    st.stop()

                data = response.json()

                # -------------------------------
                # HANDLE TEXT RESPONSE
                # -------------------------------
                ai_response = data.get("response", "")

                if ai_response:
                    placeholder.write(ai_response)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": ai_response
                    })

                # -------------------------------
                # HANDLE CHART RESPONSE
                # -------------------------------
                chart_b64 = data.get("chart_b64", None)

                if chart_b64:
                    st.image(base64.b64decode(chart_b64), caption="Visualization")

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": "",
                        "image": chart_b64
                    })

                # If backend returned nothing
                if not ai_response and not chart_b64:
                    placeholder.error("❌ No usable response received from API.")

            except Exception as e:
                error_msg = f"❌ Backend communication failed: {e}"
                placeholder.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })
