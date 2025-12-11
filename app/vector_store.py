# app/vector_store.py
import uuid
from chromadb import PersistentClient

# Initialize persistent ChromaDB
client = PersistentClient(path="data/db")

# Create (or load) collection
collection = client.get_or_create_collection(
    name="documents",
    metadata={"hnsw:space": "cosine"}
)

def add_chunks(chunks, embeddings):
    """
    Add text chunks and their embeddings to ChromaDB.
    Uses unique UUIDs for safe storage.
    """
    ids = [str(uuid.uuid4()) for _ in chunks]  # Unique IDs

    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings
    )


def search(query_embedding, top_k=5):
    """
    Query the vector database for top_k relevant chunks.
    Chroma v0.5+ DOES NOT allow include=["ids"], so removed.
    """

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "distances", "metadatas"]  # valid fields only
    )

    return results
