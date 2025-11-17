# understand_embeddings.py
from sentence_transformers import SentenceTransformer
import numpy as np

# Load a small embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Some example texts from your database
texts = [
    "Employees table with names and departments",
    "Customer data with addresses and emails", 
    "Sales records with amounts and dates",
    "Product inventory with prices",
    "Employee salaries and positions"
]

print("🔄 Creating embeddings...")
embeddings = model.encode(texts)

print(f"📊 Each text becomes a vector of {embeddings.shape[1]} numbers")
print(f"📈 We have {embeddings.shape[0]} vectors total")

# Show similarity between them
print("\n🔍 Similarity between texts (0=no similarity, 1=identical):")
for i, text1 in enumerate(texts):
    for j, text2 in enumerate(texts[i+1:], i+1):
        similarity = np.dot(embeddings[i], embeddings[j])
        print(f"  '{text1[:20]}...' vs '{text2[:20]}...' = {similarity:.3f}")