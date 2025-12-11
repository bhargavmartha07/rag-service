# app/document_processor.py
import re
import PyPDF2
import docx
import os

def extract_text(file_path: str) -> str:
    file_path = str(file_path)
    if file_path.lower().endswith(".txt"):
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    elif file_path.lower().endswith(".pdf"):
        text = ""
        try:
            reader = PyPDF2.PdfReader(file_path)
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    text += t + "\n"
        except Exception as e:
            # fallback: return empty string on failure
            print("PDF read error:", e)
        return text
    elif file_path.lower().endswith(".docx"):
        try:
            doc = docx.Document(file_path)
            return "\n".join([p.text for p in doc.paragraphs])
        except Exception as e:
            print("DOCX read error:", e)
            return ""
    else:
        raise ValueError("Unsupported file type")


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200):
    if not text:
        return []
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()
    chunks = []
    start = 0
    text_len = len(text)
    while start < text_len:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk.strip())
        if end >= text_len:
            break
        start = end - overlap
    return chunks
