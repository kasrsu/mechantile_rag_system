# test_search_real.py
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
import json

print("🚀 Connecting to YOUR ACTUAL Vector Database...")

# 1. First, let's see what's in your chunks.json
try:
    with open("chunks.json", "r") as f:
        chunks = json.load(f)
    print(f"✅ Loaded {len(chunks)} real tables from chunks.json")
    
    # Show what tables we actually have
    tables_found = [chunk['table'] for chunk in chunks]
    print(f"📊 Your actual tables: {tables_found}")
    
except FileNotFoundError:
    print("❌ chunks.json not found! Run extract.py first!")
    exit()

# 2. Connect to your REAL Chroma DB
try:
    ef = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    client = chromadb.PersistentClient(path="chroma_db")
    collection = client.get_collection(name="company_schema", embedding_function=ef)
    print(f"✅ Connected to Chroma DB - {collection.count()} chunks loaded")
    
except Exception as e:
    print(f"❌ Could not connect to Chroma DB: {e}")
    print("💡 Run build_db.py first!")
    exit()

# 3. Your REAL questions
questions = [
    "Which employees earn the most money?",
    "What products are available for sale?",
    "Show me customer contact information",
    "How many sales did we make last month?"
]

print("\n🔍 Testing Search with YOUR REAL VECTOR DB:\n")

for question in questions:
    print(f"❓ Question: '{question}'")
    
    # ACTUALLY query your vector database
    results = collection.query(
        query_texts=[question],
        n_results=2  # Top 2 most relevant tables
    )
    
    # Show results from YOUR real data
    for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
        table_name = metadata['table']
        # Show preview of the chunk
        preview = doc[:100] + "..." if len(doc) > 100 else doc
        print(f"   {i+1}. 📊 {table_name}")
        print(f"      Preview: {preview}")
        print(f"      Distance: {results['distances'][0][i]:.3f}")
    print()