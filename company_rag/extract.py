# company_rag/extract.py
import sqlite3
import json

DB_PATH = "../data/Chinook.db"  # ← CHANGE TO YOUR REAL DB LATER
CHUNK_SIZE = 3  # Sample rows per chunk

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Get all tables (limit 100 for now)
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cur.fetchall()][:100]

chunks = []
for table in tables:
    # Get columns
    cur.execute(f"PRAGMA table_info({table})")
    columns = [row[1] for row in cur.fetchall()]
    
    # Get sample rows
    cur.execute(f"SELECT * FROM {table} LIMIT {CHUNK_SIZE}")
    rows = cur.fetchall()
    if not rows:
        continue
    
    # Build chunk text
    sample_text = "\n".join([" | ".join(map(str, row)) for row in rows])
    chunk_text = f"TABLE: {table}\nCOLUMNS: {', '.join(columns)}\nSAMPLE ROWS:\n{sample_text}"
    
    chunks.append({
        "text": chunk_text,
        "table": table
    })

# Save
with open("chunks.json", "w") as f:
    json.dump(chunks, f, indent=2)

print(f"✅ Extracted {len(chunks)} chunks from {len(tables)} tables")
conn.close()