# company_rag/agent.py
from langchain_core.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from langchain.tools import tool
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
import chromadb
from langchain_ollama import ChatOllama

from tools.sql_tool import run_sql

# === LLM ===
llm = ChatOllama(model="llama3.1:8b", temperature=0)

# === Vector DB ===
embed = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="chroma_db")
coll = client.get_collection("company_schema")

# === TOOLS ===
@tool
def retrieve_schema(query: str) -> str:
    """Search for relevant tables and sample data"""
    results = coll.query(query_texts=[query], n_results=3)
    docs = results["documents"][0]
    return "\n\n---\n\n".join(docs)

@tool
def execute_sql(sql: str) -> str:
    """Run SQL on the database and return JSON result"""
    return run_sql(sql)

tools = [retrieve_schema, execute_sql]

# === PROMPT ===
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an intelligent business analyst robot for the company database.
You MUST:
1. Use 'retrieve_schema' to find relevant tables
2. Write valid SQL using exact column names
3. Use 'execute_sql' to get real data
4. Analyze trends, anomalies, or patterns
5. Suggest 3 actionable business options with proof from data

NEVER hallucinate tables or columns.
If unsure, say "I need more data" and use tools.

Answer in clear, professional English."""),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

# === AGENT ===
agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# === LIVE CHAT ===
print("🤖 INTELLIGENT ROBOT ONLINE")
print("Ask anything about the database. Type 'quit' to exit.\n")

while True:
    user_input = input("You: ").strip()
    if user_input.lower() in ["quit", "exit", "bye"]:
        print("🤖 Robot offline.")
        break
    if not user_input:
        continue

    print("\n🤖 Thinking...\n")
    try:
        result = executor.invoke({"input": user_input})
        print(f"💬 {result['output']}\n")
    except Exception as e:
        print(f"⚠️ Agent error: {e}\n")
    print("-" * 80)