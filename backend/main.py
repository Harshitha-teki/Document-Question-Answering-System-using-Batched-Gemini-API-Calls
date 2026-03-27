from fastapi import FastAPI, UploadFile, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
import os, uuid, shutil
from processor import process_document_task
from gemini_client import get_gemini_response
from fpdf import FPDF

app = FastAPI()

# Requirement 5 & 8: Data Stores
db = {"documents": {}, "sessions": {}}
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

@app.get("/health")
def health(): return {"status": "ok"}

@app.post("/upload", status_code=202)
async def upload(file: UploadFile, bg: BackgroundTasks):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".pdf", ".txt", ".docx"]:
        raise HTTPException(400, "Invalid file type")
    
    doc_id = str(uuid.uuid4())
    file_path = os.path.join(DATA_DIR, f"{doc_id}{ext}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    db["documents"][doc_id] = {"status": "processing", "chunks": [], "filename": file.filename}
    bg.add_task(process_document_task, doc_id, file_path, ext, db)
    
    return {"document_id": doc_id, "filename": file.filename, "message": "Document accepted"}

@app.get("/documents/{doc_id}/status")
def get_status(doc_id: str):
    return {"document_id": doc_id, "status": db["documents"].get(doc_id, {}).get("status", "not_found")}

@app.post("/ask")
async def ask(payload: dict):
    doc_ids = payload.get("document_ids", [])
    question = payload.get("question", "")
    session_id = payload.get("session_id", "default")
    
    # Retrieve chunks
    all_chunks = []
    for d_id in doc_ids:
        doc_data = db["documents"].get(d_id)
        if doc_data and "chunks" in doc_data:
            all_chunks.extend(doc_data["chunks"][:3])
    
    # Get history
    history = db["sessions"].get(session_id, [])
    
    # Call Gemini
    result = get_gemini_response(question, all_chunks, history)
    
    # CHECK IF API FAILED BEFORE APPENDING TO HISTORY
    if "error" in result:
        return result  # Return the error to the UI instead of crashing
        
    # Only append if we actually got an answer
    history.append({"role": "user", "content": question})
    history.append({"role": "assistant", "content": result["answer"]})
    db["sessions"][session_id] = history
    
    return {**result, "session_id": session_id}

@app.get("/session/{session_id}/export")
def export_pdf(session_id: str):
    # Requirement 10: Export to PDF
    history = db["sessions"].get(session_id, [])
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for msg in history:
        pdf.multi_cell(0, 10, txt=f"{msg['role'].upper()}: {msg['content']}")
        pdf.ln(2)
    
    path = os.path.join(DATA_DIR, f"session_{session_id}.pdf")
    pdf.output(path)
    return FileResponse(path, filename=f"session_{session_id}.pdf")