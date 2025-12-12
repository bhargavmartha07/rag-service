import re
import PyPDF2
import docx
from typing import List


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


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    if not text:
        return []

    # Normalize but preserve paragraph breaks
    text = re.sub(r'\r\n', '\n', text)
    text = re.sub(r'\n\s*\n+', '\n\n', text).strip()

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    current = ""

    for para in paragraphs:
        if len(current) + len(para) + 1 <= chunk_size:
            current = (current + " " + para).strip()
        else:
            if current:
                chunks.append(current.strip())
            if len(para) > chunk_size:
                start = 0
                while start < len(para):
                    end = start + chunk_size
                    chunks.append(para[start:end].strip())
                    if end >= len(para):
                        break
                    start = end - overlap
                current = ""
            else:
                current = para

    if current:
        chunks.append(current.strip())

    # create small overlap between adjacent chunks
    if overlap > 0 and len(chunks) > 1:
        merged = []
        for i, c in enumerate(chunks):
            if i == 0:
                merged.append(c)
            else:
                prev = merged[-1]
                tail = prev[-overlap:] if len(prev) > overlap else prev
                merged.append((tail + " " + c).strip())
        chunks = merged

    return chunks
