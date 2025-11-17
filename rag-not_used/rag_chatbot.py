# rag/rag_chatbot.py
import json
import re

try:
    import ollama
    from ollama import Client
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    print("Warning: ollama module not available. LLM features disabled.")

MODEL = "corpgpt-sales"
SUMMARY_FILE = "summary_cache.json"  # Changed from "rag/summary_cache.json"

# Load summaries
try:
    with open(SUMMARY_FILE) as f:
        CACHE = json.load(f)["data"]
except:
    print("Run summaries.py first!")
    exit(1)

def rag_answer(query):
    if not OLLAMA_AVAILABLE:
        return "LLM features disabled due to missing ollama module."
    
    q = query.lower()

    # === FAST PATH: Direct from cache ===
    if "2013" in q and "sales" in q:
        return f"Total sales in 2013: ${CACHE['yearly_sales'].get('2013', 'N/A'):.2f}"
    
    if "top genre" in q:
        top = CACHE["top_genres"][0]
        return f"Top genre: {top[0]} with ${top[1]:.2f} in revenue."
    
    if "top customer" in q:
        top = CACHE["top_customers"][0]
        return f"Top customer: {top[0]} (${top[1]:.2f})"

    # === SLOW PATH: LLM + SQL ===
    response = ollama.chat(model=MODEL, messages=[
        {'role': 'user', 'content': query}
    ])
    raw = response['message']['content'].strip()
    raw = re.sub(r"^```json\n|```$", "", raw, flags=re.MULTILINE).strip()

    try:
        data = json.loads(raw)
        return f"SQL: {data['query']}\n→ {data['explanation']}"
    except:
        return "Sorry, I couldn't process that. Try: 'sales in 2013', 'top genre'"

# === LIVE CHAT ===
def main():
    print("🚀 Merchantile RAG v2 – Fast + Smart")
    print("Ask: 'sales 2013', 'top genre', or anything\n")

    while True:
        q = input("You: ").strip()
        if q.lower() in ['quit', 'exit']:
            break
        if not q: continue

        print("⚡ Thinking...")
        ans = rag_answer(q)
        print(f"\n💬 {ans}\n" + "-"*50 + "\n")

if __name__ == "__main__":
    main()