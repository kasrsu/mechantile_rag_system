# save as test_ollama.py
import ollama
import requests

# Raw API test
try:
    r = requests.get("http://localhost:11434/api/tags")
    print("RAW API:", r.json())
except Exception as e:
    print("API DOWN:", e)

# Ollama client test
try:
    models = ollama.list()
    print("OLLAMA LIST:", models)
except Exception as e:
    print("OLLAMA CLIENT ERROR:", e)