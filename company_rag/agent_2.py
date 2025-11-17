# company_rag/agent.py
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.tools import tool
from langchain_community.embeddings import SentenceTransformerEmbeddings
import chromadb
from langchain_ollama import ChatOllama
import json

from tools.sql_tool import run_sql

# === LLM ===
llm = ChatOllama(model="qwen2.5-coder:7b", temperature=0)

# === Vector DB ===
embed = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="chroma_db")
coll = client.get_collection("company_schema")

# === TOOLS ===
def retrieve_schema(query: str) -> str:
    """Search for relevant tables and sample data"""
    print(f"🔍 [RETRIEVE_SCHEMA] Searching for: '{query}'")
    results = coll.query(query_texts=[query], n_results=3)
    docs = results["documents"][0]
    print(f"✓ [RETRIEVE_SCHEMA] Found {len(docs)} relevant schema entries")
    return "\n\n---\n\n".join(docs)

def execute_sql(sql: str) -> str:
    """Run SQL on the database and return JSON result"""
    print(f"⚙️ [EXECUTE_SQL] Running query:")
    print(f"   {sql}")
    result = run_sql(sql)
    print(f"✓ [EXECUTE_SQL] Query completed successfully")
    return result

# === PROMPT ===
prompt = ChatPromptTemplate.from_messages([
    ("system","""You are an expert SQL analyst with access to a Chinook database.

Available tools:
1. retrieve_schema - Search for table schemas and sample data
2. execute_sql - Execute SQL queries and get real results

TOOL CALLING FORMAT (you MUST use this exact format):
TOOL: tool_name
ARGS: your_argument_here

Example 1 - Retrieve schema:
TOOL: retrieve_schema
ARGS: sales revenue invoice

Example 2 - Execute SQL:
TOOL: execute_sql
ARGS: SELECT strftime('%Y', InvoiceDate) as Year, SUM(Total) as Revenue FROM Invoice GROUP BY Year ORDER BY Year DESC LIMIT 5

PROCESS (follow strictly):
1. First, call retrieve_schema to find relevant tables
2. After seeing schema results, write ONE valid SQLite query
3. Call execute_sql with that exact query
4. After getting real data, provide analysis with 3 numbered suggestions

IMPORTANT RULES:
- Use strftime('%Y', column_name) for extracting years from dates
- NEVER give analysis without executing SQL first
- Database has data up to 2013, NOT 2024
- Always wait for tool results before proceeding
- Each tool call must be on separate lines

Tables: Invoice, InvoiceLine, Customer, Track, Album, Genre, Artist, Employee, Playlist, PlaylistTrack, MediaType

"""),
    ("user", "{input}"),
    ("assistant", "{history}"),
])

chain = prompt | llm | StrOutputParser()

# === LIVE CHAT ===
print("=" * 80)
print("🤖 INTELLIGENT BUSINESS ANALYST ROBOT")
print("=" * 80)
print("💡 Ask anything about the database")
print("💡 Type 'quit', 'exit', or 'bye' to stop\n")

while True:
    print("─" * 80)
    user_input = input("👤 You: ").strip()
    
    if user_input.lower() in ["quit", "exit", "bye"]:
        print("\n" + "=" * 80)
        print("🤖 Robot shutting down. Goodbye!")
        print("=" * 80)
        break
        
    if not user_input:
        continue

    print("\n" + "─" * 80)
    print("🤖 [AGENT] Processing your request...")
    print("─" * 80 + "\n")
    
    history = ""
    max_iterations = 5
    
    for iteration in range(max_iterations):
        try:
            print(f"🔄 [ITERATION {iteration + 1}/{max_iterations}]")
            response = chain.invoke({"input": user_input, "history": history})
            
            # Check if agent wants to use a tool
            if "TOOL:" in response and "ARGS:" in response:
                print(f"🧠 [AGENT] Decided to use a tool\n")
                
                lines = response.split("\n")
                tool_name = None
                args_lines = []
                capturing_args = False
                
                for line in lines:
                    if line.startswith("TOOL:"):
                        tool_name = line.replace("TOOL:", "").strip()
                        capturing_args = False
                    elif line.startswith("ARGS:"):
                        args_lines.append(line.replace("ARGS:", "").strip())
                        capturing_args = True
                    elif capturing_args and line.strip() and not line.startswith("TOOL:"):
                        args_lines.append(line.strip())
                    elif line.startswith("TOOL:") or (capturing_args and not line.strip()):
                        break
                
                args = " ".join(args_lines) if args_lines else None
                
                if tool_name and args:
                    print(f"🔧 [TOOL CALL] {tool_name}")
                    print(f"📝 [ARGUMENTS] {args}\n")
                    
                    if tool_name == "retrieve_schema":
                        result = retrieve_schema(args)
                    elif tool_name == "execute_sql":
                        result = execute_sql(args)
                    else:
                        result = f"Unknown tool: {tool_name}"
                        print(f"❌ [ERROR] {result}")
                    
                    print(f"\n📊 [TOOL RESULT]")
                    print("─" * 80)
                    print(result)
                    print("─" * 80 + "\n")
                    
                    history += f"\n\nTool {tool_name} returned:\n{result}\n"
                else:
                    break
            else:
                # Final answer
                print("✅ [AGENT] Generated final answer\n")
                print("=" * 80)
                print("💬 RESPONSE:")
                print("=" * 80)
                print(response)
                print("=" * 80 + "\n")
                break
                
        except Exception as e:
            print(f"\n❌ [ERROR] {str(e)}")
            print("=" * 80 + "\n")
            break
    
    if iteration == max_iterations - 1:
        print(f"⚠️ [WARNING] Reached maximum iterations ({max_iterations})\n")