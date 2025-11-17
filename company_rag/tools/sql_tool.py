# company_rag/tools/sql_tool.py
import sqlite3
import json

DB_PATH = "../data/Chinook.db"  # ← Swap with real DB later

def run_sql(sql: str) -> str:
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        cols = [desc[0] for desc in cur.description]
        result = [dict(zip(cols, row)) for row in rows][:20]  # Cap output
        conn.close()
        return json.dumps({
            "data": result,
            "count": len(result),
            "truncated": len(result) == 20
        }, indent=2)
    except Exception as e:
        return f"SQL ERROR: {str(e)}"