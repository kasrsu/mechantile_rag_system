# rag/chatbot.py
import json
import sqlite3
import ollama
from ollama import Client  # optional, but cleaner

DB_PATH = "../data/Chinook.db"
MODEL = "corpgpt-sales"

# === SQL EXECUTOR ===
def execute_sql(sql):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        cols = [desc[0] for desc in cur.description]
        result = [dict(zip(cols, row)) for row in rows]
        conn.close()
        return {"data": result, "row_count": len(result)}
    except Exception as e:
        return {"error": str(e)}

# === LLM SQL GENERATOR ===
def generate_sql(query):
    response = ollama.chat(model=MODEL, messages=[
        {'role': 'user', 'content': query}
    ])
    try:
        return json.loads(response['message']['content'])
    except:
        return {"error": "LLM didn't return valid JSON"}

# === EXPLAIN RESULT ===
def explain_result(sql, result):
    if "error" in result:
        return f"SQL Error: {result['error']}"

    prompt = f"""
    SQL: {sql}
    RESULT: {json.dumps(result['data'][:10], indent=2)}  # cap at 10 rows
    ROWS: {result['row_count']}
    
    Explain in 1-2 sentences. Business English. No jargon.
    """
    resp = ollama.chat(model=MODEL, messages=[
        {'role': 'system', 'content': 'You are a sales analyst. Be concise.'},
        {'role': 'user', 'content': prompt}
    ])
    return resp['message']['content'].strip()

# === MAIN CHAT LOOP ===
def main():
    print("🛒 Merchantile RAG Chatbot – Ask about Chinook sales")
    print("Type 'quit' to exit\n")

    while True:
        user_query = input("You: ").strip()
        if user_query.lower() in ['quit', 'exit', 'bye']:
            print("Logged out. Phase 3 active.")
            break
        if not user_query:
            continue

        print("🤖 Generating SQL...")
        json_resp = generate_sql(user_query)
        
        if "error" in json_resp:
            print(f"⚠️ LLM Error: {json_resp['error']}")
            continue
        
        sql = json_resp.get("query", "").strip()
        if not sql:
            print("⚠️ No SQL generated.")
            continue

        print(f"🔍 Running: {sql}")
        result = execute_sql(sql)

        explanation = explain_result(sql, result)
        
        print("\n📊 RESULT:")
        if "error" in result:
            print(f"❌ DB Error: {result['error']}")
        else:
            print(json.dumps(result["data"][:5], indent=2))  # show first 5
            if result["row_count"] > 5:
                print(f"... +{result['row_count'] - 5} more rows")
        
        print(f"\n💬 {explanation}")
        print("\n" + "-"*60 + "\n")

if __name__ == "__main__":
    main()