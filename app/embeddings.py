# app/embeddings.py
from sentence_transformers import SentenceTransformer

# load once
_model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_text(text_list):
    """
    Accepts list[str] and returns list[list[float]] compatible with Chroma.
    """
    if not text_list:
        return []
    embeddings = _model.encode(text_list, show_progress_bar=False)
    # convert to nested lists (python lists)
    return embeddings.tolist() if hasattr(embeddings, "tolist") else [list(e) for e in embeddings]
