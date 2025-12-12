import os
from sentence_transformers import SentenceTransformer

_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

try:
    model = SentenceTransformer(_MODEL_NAME)
except Exception as e:
    raise RuntimeError(f"Failed to load embedding model {_MODEL_NAME}: {e}")


def embed_text(text_list):
    """
    Accepts list[str] -> returns list[list[float]] suitable for storing.
    """
    if not isinstance(text_list, list):
        text_list = [text_list]
    embs = model.encode(text_list, show_progress_bar=False)
    # convert to python lists
    return embs.tolist()
