import os
import sqlite3
from typing import List
from dotenv import load_dotenv
from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from datetime import datetime

# Load TogetherAI key
load_dotenv()
api_key = os.getenv("TOGETHER_API_KEY")
if not api_key:
    raise ValueError("Missing TOGETHER_API_KEY in .env")

# LangChain model setup
llm = ChatOpenAI(
    model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
    base_url="https://api.together.xyz/v1",
    api_key=api_key,
    temperature=0
)

# Database setup
db_path = "retail_store.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# ---------- Tool Definitions ----------

@tool
def get_current_datetime(dummy: str = "") -> str:
    """
    Returns the current date and time in the format YYYY-MM-DD HH:MM:SS.
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@tool
def query_db(sql: str) -> str:
    """Executes a given SQL command and returns the result."""
    try:
        cursor.execute(sql)
        if sql.strip().lower().startswith("select"):
            rows = cursor.fetchall()
            headers = [desc[0] for desc in cursor.description]
            if not rows:
                return "No rows found."
            return "\n".join([", ".join(headers)] + [", ".join(map(str, row)) for row in rows])
        else:
            conn.commit()
            return "✅ SQL executed successfully."
    except Exception as e:
        return f"❌ SQL execution error: {e}"

@tool
def get_column_values(input_str: str) -> List[str]:
    """
    Fetches all distinct values from a column in a table.
    Input format: "table,column"
    Example: "departments,department_name"
    """
    try:
        table, column = input_str.split(",")
        cursor.execute(f"SELECT DISTINCT {column.strip()} FROM {table.strip()}")
        rows = cursor.fetchall()
        return [str(row[0]) for row in rows]
    except Exception as e:
        return [f"❌ Error fetching values: {e}"]

@tool
def get_schema(dummy: str = "") -> str:
    """Returns the schema of all tables."""
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        schema = ""
        for (table,) in tables:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            schema += f"\nTable: {table}\n"
            schema += "\n".join([f"  - {col[1]} ({col[2]})" for col in columns]) + "\n"
        return schema.strip()
    except Exception as e:
        return f"❌ Error fetching schema: {e}"

tools = [query_db, get_column_values, get_schema, get_current_datetime]

# ---------- Prompt Setup ----------

prompt_template_str = """
You are a helpful and intelligent assistant that helps users interact with a company employee database.

You have access to the following tools:
{tools}

Here are the tool names:
{tool_names}

Use the following format:

Question: the input question you must answer  
Thought: think about what to do, you can use the tools to get the information you need, then use the information to answer the question.
Action: the action to take, should be one of [{tool_names}]  
Action Input: the input to the action  
Observation: the result of the action  
... (repeat Thought/Action/Action Input/Observation as needed)  
Thought: I now know the final answer  
Final Answer: the final answer to the original question in well formatted descriptive answer or tables as needed.

Begin!

Question: {input}
{agent_scratchpad}
"""

prompt = PromptTemplate(
    input_variables=["input", "tools", "tool_names", "agent_scratchpad"],
    template=prompt_template_str
)

# ---------- Agent Build ----------

agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

# ---------- Schema Helper ----------

def fetch_schema() -> str:
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        schema = ""
        for (table,) in tables:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            schema += f"\nTable: {table}\n"
            schema += "\n".join([f"  - {col[1]} ({col[2]})" for col in columns]) + "\n"
        return schema.strip()
    except Exception as e:
        return f"❌ Error fetching schema: {e}"

# ---------- Main Interaction ----------

def main():
    print("🧠 NLP-to-SQL LangChain Agent (Dynamic + Recursive + Smart)")
    print("Type 'exit' to quit. Ask anything about your company database.")
    while True:
        user_input = input("\n💬 Ask your question: ").strip()
        if user_input.lower() in ['exit', 'quit']:
            break
        try:
            schema_info = fetch_schema()
            input_with_schema = f"The current database schema is:\n{schema_info}\n\nNow answer this:\n{user_input}"
            result = agent_executor.invoke({"input": input_with_schema})
            print("\n🧾 Final Result:")
            print(result["output"])
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
