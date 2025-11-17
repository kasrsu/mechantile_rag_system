# rag/summaries.py
import sqlite3
import json
from datetime import datetime

DB_PATH = "../data/Chinook.db"

def generate_summaries():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    summaries = {}

    # 1. Yearly sales
    cur.execute("""
        SELECT strftime('%Y', InvoiceDate) AS year, SUM(Total) AS sales
        FROM Invoice GROUP BY year ORDER BY year
    """)
    summaries["yearly_sales"] = {row[0]: row[1] for row in cur.fetchall()}

    # 2. Top genres
    cur.execute("""
        SELECT g.Name, SUM(il.Quantity * il.UnitPrice) AS revenue
        FROM Genre g
        JOIN Track t ON g.GenreId = t.GenreId
        JOIN InvoiceLine il ON t.TrackId = il.TrackId
        GROUP BY g.Name ORDER BY revenue DESC LIMIT 5
    """)
    summaries["top_genres"] = [(row[0], row[1]) for row in cur.fetchall()]

    # 3. Top customers
    cur.execute("""
        SELECT c.FirstName || ' ' || c.LastName AS name, SUM(i.Total) AS spend
        FROM Customer c JOIN Invoice i ON c.CustomerId = i.CustomerId
        GROUP BY c.CustomerId ORDER BY spend DESC LIMIT 5
    """)
    summaries["top_customers"] = [(row[0], row[1]) for row in cur.fetchall()]

    # Save
    # Save
    with open("summary_cache.json", "w") as f:  # Changed from "rag/summary_cache.json"
        json.dump({
            "generated_at": datetime.now().isoformat(),
            "data": summaries
        }, f, indent=2)
    
    print("Summaries cached: summary_cache.json")  # Updated message
    conn.close()

if __name__ == "__main__":
    generate_summaries()