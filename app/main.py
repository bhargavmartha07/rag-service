from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import uuid
from typing import List

from app.document_processor import extract_text, chunk_text
from app.embeddings import embed_text
from app.vector_store import add_chunks, search, collection_or_info
from app.llm import generate_answer

app = FastAPI(title="RAG Service")

# CORS - allow local frontend to call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# constants
UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def sanitize_filename(filename: str) -> str:
    return f"{uuid.uuid4().hex}_{os.path.basename(filename)}"


@app.post("/upload", status_code=201)
async def upload_documents(files: List[UploadFile] = File(...)):
    """
    Accepts multiple files: pdf, txt, docx.
    Stores on disk, extracts text, chunks, embeds and stores vectors.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    total_chunks = 0
    for file in files:
        if not file.filename:
            continue
        ext = file.filename.split(".")[-1].lower()
        if ext not in ["pdf", "txt", "docx"]:
            raise HTTPException(status_code=400, detail=f"Invalid file type: {file.filename}")

        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail=f"File too large: {file.filename}")

        safe_name = sanitize_filename(file.filename)
        file_path = os.path.join(UPLOAD_DIR, safe_name)
        with open(file_path, "wb") as f:
            f.write(content)

        # extract, chunk, embed, store
        text = extract_text(file_path)
        chunks = chunk_text(text)
        if not chunks:
            continue
        embeddings = embed_text(chunks)
        add_chunks(chunks, embeddings, metadata=[{"source": file.filename} for _ in chunks])
        total_chunks += len(chunks)

    return {"message": "Documents uploaded successfully", "total_chunks": total_chunks}


@app.post("/query")
async def ask_question(payload: dict):
    """
    Query payload: {"question": "..." }
    Returns {"answer": "...", "sources": [...]}
    """
    question = payload.get("question") if isinstance(payload, dict) else None
    if not question:
        raise HTTPException(status_code=400, detail="Question is required")

    q_emb = embed_text([question])[0]
    results = search(q_emb, top_k=5)

    # results format (both for chroma or faiss fallback): results["documents"] -> list of lists
    documents = results.get("documents", [])
    if not documents or len(documents) == 0:
        return {"answer": "The document does not contain this information.", "sources": []}

    retrieved_chunks = documents[0]  # list[str]
    answer = generate_answer(retrieved_chunks, question)

    return {"answer": answer, "sources": retrieved_chunks}


@app.get("/report")
async def report():
    """Return a small usage / evaluation report (hardcoded metrics as requested)."""
    try:
        docs = collection_or_info()
        total_chunks = docs.get("total_chunks", 0)
    except Exception:
        total_chunks = 0

    return {
        "total_documents": len(os.listdir(UPLOAD_DIR)),
        "total_chunks": total_chunks,
        "top_k": 5,
        "context_precision": 0.9,
        "faithfulness": 0.85,
    }


# Serve frontend static site (must be last)
if os.path.isdir("frontend"):
    app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
else:
    # If frontend directory missing, server still runs API endpoints
    pass
