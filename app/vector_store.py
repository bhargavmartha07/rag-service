import os
import uuid
import pickle
import numpy as np

# try chromadb first
USE_CHROMA = False
collection = None

try:
    import chromadb
    # try to create a persistent client
    DB_DIR = "data/db"
    os.makedirs(DB_DIR, exist_ok=True)
    try:
        client = chromadb.PersistentClient(path=DB_DIR)
        collection = client.get_or_create_collection(name="documents", metadata={})
        USE_CHROMA = True
    except Exception:
        # chroma failed (version / migration); we'll fallback
        USE_CHROMA = False
except Exception:
    USE_CHROMA = False

# ---------------------------------------------------------------------
# FAISS fallback (file-backed)
# ---------------------------------------------------------------------
FAISS_DIR = "data/faiss"
os.makedirs(FAISS_DIR, exist_ok=True)
FAISS_STATE = os.path.join(FAISS_DIR, "state.pkl")


def _ensure_faiss():
    """
    Ensures in-memory lists and optionally an index are loaded.
    We store:
      - docs: list[str]
      - embeddings: numpy.ndarray (n x d)
      - metadatas: list[dict]
    """
    if os.path.exists(FAISS_STATE):
        with open(FAISS_STATE, "rb") as f:
            state = pickle.load(f)
            return state["docs"], state["embeddings"], state.get("metadatas", [])
    else:
        return [], np.zeros((0, 384), dtype=np.float32), []


def _save_faiss(docs, embeddings, metadatas):
    with open(FAISS_STATE, "wb") as f:
        pickle.dump({"docs": docs, "embeddings": embeddings, "metadatas": metadatas}, f)


def _cosine_similarity(a, b):
    # a: (d,), b: (n, d) -> returns (n,)
    # ensure float32
    a = np.array(a, dtype=np.float32)
    b = np.array(b, dtype=np.float32)
    if np.linalg.norm(a) == 0:
        return np.zeros(b.shape[0], dtype=np.float32)
    a_norm = a / (np.linalg.norm(a) + 1e-12)
    b_norm = b / (np.linalg.norm(b, axis=1, keepdims=True) + 1e-12)
    return (b_norm @ a_norm).astype(np.float32)


def add_chunks(chunks, embeddings, metadata=None):
    """
    Add chunk texts and their embeddings.
    If chroma is enabled, forward to chroma. Otherwise, store in a pickle-backed list.
    """
    global collection
    if USE_CHROMA and collection is not None:
        ids = [str(uuid.uuid4()) for _ in chunks]
        if metadata and len(metadata) == len(chunks):
            collection.add(ids=ids, documents=chunks, embeddings=embeddings, metadatas=metadata)
        else:
            collection.add(ids=ids, documents=chunks, embeddings=embeddings)
        return

    # FAISS fallback
    docs, embs, metadatas = _ensure_faiss()
    embs_new = np.array(embeddings, dtype=np.float32)
    if embs.size == 0:
        embs = embs_new
    else:
        embs = np.vstack([embs, embs_new])
    docs.extend(chunks)
    if metadata and len(metadata) == len(chunks):
        metadatas.extend(metadata)
    else:
        metadatas.extend([{} for _ in chunks])
    _save_faiss(docs, embs, metadatas)


def search(query_embedding, top_k=5):
    """
    Return a uniform results dict:
      {"documents": [[...strings...]], "distances": [[...floats...]], "metadatas": [...]}
    """
    global collection
    if USE_CHROMA and collection is not None:
        res = collection.query(query_embeddings=[query_embedding], n_results=top_k, include=["documents", "distances", "metadatas"])
        # chroma returns lists-of-lists; keep same shape
        return res

    # FAISS fallback: brute-force cosine
    docs, embs, metadatas = _ensure_faiss()
    if len(docs) == 0:
        return {"documents": [[]], "distances": [[]], "metadatas": [[]], "total_chunks": 0}

    sims = _cosine_similarity(query_embedding, embs)  # (n,)
    idx_sorted = np.argsort(-sims)[:top_k]
    found_docs = [docs[i] for i in idx_sorted]
    found_sims = [float(sims[i]) for i in idx_sorted]
    found_meta = [metadatas[i] for i in idx_sorted] if metadatas else [{} for _ in idx_sorted]
    return {"documents": [found_docs], "distances": [found_sims], "metadatas": [found_meta], "total_chunks": len(docs)}


def collection_or_info():
    """
    Returns a small info dict for /report endpoint with total_chunks.
    """
    if USE_CHROMA and collection is not None:
        docs = collection.get(include=["documents"])
        total = len(docs.get("documents", []))
        return {"total_chunks": total}
    else:
        docs, embs, _ = _ensure_faiss()
        return {"total_chunks": len(docs)}
