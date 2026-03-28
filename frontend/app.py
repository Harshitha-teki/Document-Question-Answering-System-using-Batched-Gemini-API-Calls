import streamlit as st
import requests
import time
import os

# Internal Docker communication (Container to Container)
API_URL = "http://api:8000"
# External Browser communication (Host to Container)
USER_DOWNLOAD_URL = "http://localhost:8000"

st.set_page_config(page_title="Gemini Doc Q&A | VEDA 2K26", layout="wide")
st.title("📄 Document Q&A System (Gemini Batched)")

# Session State Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []
if "document_id" not in st.session_state:
    st.session_state.document_id = None
if "session_id" not in st.session_state:
    st.session_state.session_id = f"session_{int(time.time())}"

# Sidebar for Upload & Actions
with st.sidebar:
    st.header("Upload Document")
    uploaded_file = st.file_uploader("Choose a file", type=['pdf', 'docx', 'txt'])
    
    if uploaded_file and st.button("Process Document"):
        with st.spinner("Uploading and Chunking..."):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
            res = requests.post(f"{API_URL}/upload", files=files)
            if res.status_code == 202:
                doc_id = res.json()["document_id"]
                st.session_state.document_id = doc_id
                
                # Requirement 5: Polling Status
                status = "processing"
                progress_bar = st.progress(0)
                while status == "processing":
                    time.sleep(2)
                    status_res = requests.get(f"{API_URL}/documents/{doc_id}/status")
                    status = status_res.json().get("status", "failed")
                    progress_bar.progress(50)
                
                if status == "completed":
                    progress_bar.progress(100)
                    st.success("Document Ready!")
                else:
                    st.error("Processing Failed.")
    
    st.divider()
    # Requirement 10: Export Conversation to PDF
    if st.session_state.messages:
        st.header("Actions")
        export_url = f"{USER_DOWNLOAD_URL}/session/{st.session_state.session_id}/export"
        if st.button("Generate Export Link"):
            st.info(f"✅ [Click here to Download PDF Report]({export_url})")

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

        # Requirement 7: Ask Question (Batched Context)
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
                    
                    if "error" in data:
                        st.error(f"Gemini API Error: {data['error']}")
                    else:
                        answer = data.get("answer", "No response generated.")
                        st.markdown(answer)
                        
                        # Requirement 9: Real-time Token Tracking
                        tokens = data.get("tokens_used", {})
                        total = tokens.get("total_tokens", 0)
                        batch = data.get("batch_size", 0)
                        st.caption(f"📊 Tokens Used: {total} | Context Chunks: {batch}")
                        
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    st.error(f"Server Error: {response.status_code}")
            except Exception as e:
                st.error(f"Connection Error: {e}")