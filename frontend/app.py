import streamlit as st
import requests
import time

# Use the service name 'api' defined in docker-compose
API_URL = "http://api:8000"

st.set_page_config(page_title="Gemini Doc Q&A", layout="wide")
st.title("📄 Document Q&A System (Gemini Batched)")

# Session State Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []
if "document_id" not in st.session_state:
    st.session_state.document_id = None
if "session_id" not in st.session_state:
    st.session_state.session_id = "session_" + str(int(time.time()))

# Sidebar for Upload & Actions
with st.sidebar:
    st.header("Upload Document")
    uploaded_file = st.file_uploader("Choose a file", type=['pdf', 'docx', 'txt'])
    
    if uploaded_file and st.button("Process Document"):
        with st.spinner("Uploading..."):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
            res = requests.post(f"{API_URL}/upload", files=files)
            if res.status_code == 202:
                doc_id = res.json()["document_id"]
                st.session_state.document_id = doc_id
                
                # Requirement 5: Polling Status
                status = "processing"
                while status == "processing":
                    time.sleep(2)
                    status_res = requests.get(f"{API_URL}/documents/{doc_id}/status")
                    status = status_res.json()["status"]
                
                if status == "completed":
                    st.success("Document Ready!")
                else:
                    st.error("Processing Failed.")
    
    st.divider()
    # Requirement 10: Export Conversation to PDF
    if st.session_state.messages:
        st.header("Actions")
        export_url = f"{API_URL}/session/{st.session_state.session_id}/export"
        if st.button("Generate Export Link"):
            st.info(f"Click to download: [Download PDF]({export_url})")

# Chat Interface
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask a question about your document"):
    if not st.session_state.document_id:
        st.error("Please upload a document first!")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Requirement 7: Ask Question (Batched)
        payload = {
            "session_id": st.session_state.session_id,
            "document_ids": [st.session_state.document_id],
            "question": prompt
        }
        
        with st.chat_message("assistant"):
            try:
                response = requests.post(f"{API_URL}/ask", json=payload)
                if response.status_code == 200:
                    data = response.json()
                    
                    # Safety Check for API Errors (Fixes your KeyError)
                    if "error" in data:
                        st.error(f"Gemini API Error: {data['error']}")
                    else:
                        answer = data.get("answer", "I couldn't generate an answer.")
                        st.markdown(answer)
                        
                        # Requirement 9: Show Token Usage safely
                        tokens = data.get("tokens_used", {})
                        total = tokens.get("total_tokens", 0)
                        batch = data.get("batch_size", 0)
                        st.caption(f"Tokens Used: {total} | Chunks Batched: {batch}")
                        
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    st.error(f"Server Error: {response.status_code}")
            except Exception as e:
                st.error(f"Connection Error: {e}")