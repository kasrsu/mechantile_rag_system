# company_rag/build_db.py
import json
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

# Load chunks
with open("chunks.json") as f:
    chunks = json.load(f)

# Embedding model (local, fast)
ef = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

# Chroma DB
client = chromadb.PersistentClient(path="chroma_db")
collection = client.create_collection(
    name="company_schema",
    embedding_function=ef
)

# Add chunks
collection.add(
    documents=[c["text"] for c in chunks],
    metadatas=[{"table": c["table"]} for c in chunks],
    ids=[f"chunk_{i}" for i in range(len(chunks))]
)

print(f"✅ Vector DB built: {collection.count()} chunks in 'chroma_db/'")