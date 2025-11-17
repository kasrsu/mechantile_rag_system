# company_rag/test_search.py
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

# Load our vector DB
ef = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_collection(name="company_schema", embedding_function=ef)

# Test searches
test_questions = [
    "employees and their information",
    "sales and revenue data", 
    "customer details and contacts",
    "products and inventory"
]

for question in test_questions:
    print(f"\n🔍 Searching for: '{question}'")
    results = collection.query(
        query_texts=[question],
        n_results=2  # Top 2 matches
    )
    
    for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
        print(f"   {i+1}. Table: {metadata['table']}")
        print(f"      Preview: {doc[:100]}...")