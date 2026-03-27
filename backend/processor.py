import os
from PyPDF2 import PdfReader
from docx import Document
import uuid

def extract_text(file_path, extension):
    text = ""
    if extension == ".pdf":
        reader = PdfReader(file_path)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    elif extension == ".docx":
        doc = Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    elif extension == ".txt":
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    return text

def chunk_text(text, chunk_size=1000, overlap=100):
    """Requirement 6: Split text into numbered chunks"""
    chunks = []
    words = text.split()
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk_words = words[i : i + chunk_size]
        chunk_content = " ".join(chunk_words)
        chunks.append({
            "chunk_id": len(chunks),
            "text": chunk_content
        })
    return chunks

async def process_document_task(doc_id, file_path, extension, db):
    try:
        text = extract_text(file_path, extension)
        chunks = chunk_text(text)
        
        # Update our in-memory DB
        db["documents"][doc_id]["chunks"] = chunks
        db["documents"][doc_id]["status"] = "completed"
    except Exception as e:
        print(f"Error processing {doc_id}: {e}")
        db["documents"][doc_id]["status"] = "failed"