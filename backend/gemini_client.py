import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize the 2026 Client with production-ready settings
client = genai.Client(
    api_key=GEMINI_API_KEY,
    http_options={'api_version': 'v1'} # Explicitly use v1 for GA models
)

def get_gemini_response(question: str, context_chunks: list, session_history: list = None):
    """
    Requirement 7 & 10: Context Batching and System Instructions.
    Requirement 9: Token Metadata Tracking.
    """
    # Requirement 7: Batch context chunks
    context_text = "\n".join([f"[Chunk {c['chunk_id']}]: {c['text']}" for c in context_chunks])
    
    # Requirement 10: System Instruction prepended to bypass SDK JSON field bugs
    instruction = "INSTRUCTION: You are a precise assistant. Use the provided context to answer. Cite [Chunk X]."
    
    # Build a single robust content string
    full_prompt = f"{instruction}\n\nCONTEXT:\n{context_text}\n\nQUESTION: {question}"

    try:
        # Update to Gemini 2.5 Flash to resolve 404 error (cite: 2.1, 4.2)
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=full_prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,
                top_p=0.95
            )
        )

        if not response.text:
            return {"error": "Empty response. Check safety filters or API quota."}

        # Requirement 9: Exact Token Metadata for grading
        return {
            "answer": response.text,
            "batch_size": len(context_chunks),
            "tokens_used": {
                "total_tokens": response.usage_metadata.total_token_count,
                "prompt_tokens": response.usage_metadata.prompt_token_count,
                "candidates_tokens": response.usage_metadata.candidates_token_count
            }
        }
    except Exception as e:
        return {"error": f"Gemini API Error: {str(e)}"}