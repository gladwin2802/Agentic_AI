import os
import sqlite3
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from typing import List

# Load Together API key
load_dotenv()
api_key = os.getenv("TOGETHER_API_KEY")
if not api_key:
    raise ValueError("TOGETHER_API_KEY not found in .env file.")

# LangChain LLM setup
llm = ChatOpenAI(
    model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
    base_url="https://api.together.xyz/v1",
    api_key=api_key,
    temperature=0.0
)

def get_schema_from_db(db_path: str) -> str:
    """Extract schema from SQLite database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    schema_parts: List[str] = []
    schema_parts.append("You are an intelligent assistant that translates user instructions into optimized SQLite queries based on the schema below.\n")
    schema_parts.append("Schema:")
    
    for table in tables:
        table_name = table[0]
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        
        schema_parts.append(f"\nTable: {table_name}")
        for col in columns:
            name = col[1]
            type_ = col[2]
            notnull = "NOT NULL" if col[3] else ""
            pk = "PRIMARY KEY" if col[5] == 1 else ""
            constraints = " ".join(filter(None, [notnull, pk]))
            schema_parts.append(f"- {name} {type_} {constraints}".strip())
            
    # Get foreign key relationships
    for table in tables:
        table_name = table[0]
        cursor.execute(f"PRAGMA foreign_key_list({table_name});")
        fks = cursor.fetchall()
        
        for fk in fks:
            from_col = fk[3]
            to_table = fk[2]
            to_col = fk[4]
            schema_parts.append(f"Foreign Key: {table_name}.{from_col} references {to_table}({to_col})")
    
    conn.close()
    return "\n".join(schema_parts)

# Get schema from database
DB_PATH = "retail_store.db"
schema = get_schema_from_db(DB_PATH)

# Add additional instructions to schema
schema += """

Generate optimized SQL queries following these guidelines:
1. If the request has multiple parts, write multiple SQL statements separated by semicolons and new lines.
2. Use appropriate indexes and JOIN strategies (INNER, LEFT, RIGHT) based on the data relationships
3. Use meaningful table aliases (e.g., 'c' for customers, 'o' for orders)
4. Include column aliases for computed values or aggregations accordingly
5. Use appropriate WHERE clauses to filter data early in the execution
6. Consider using subqueries or CTEs (Common Table Expressions) for complex operations
7. Group and order results meaningfully when aggregating data
8. Use LIMIT when returning large result sets if not specified by the user

After ALL queries, provide a brief simple explanation of:
- Why specific JOIN types were chosen
- Any performance considerations
- How the query handles edge cases

Format your response as:
SQL:
<your SQL queries here>

EXPLANATION:
<your detailed explanation here>
"""

# Prompt template
prompt = PromptTemplate.from_template(schema + "\n\nUser Input: {input}\nResponse:")

# LangChain SQL generation chain
chain = LLMChain(llm=llm, prompt=prompt)

def main():
    print("Natural Language to SQL Converter")
    print("Converts your questions into optimized SQL queries with explanations.")
    print("Type 'exit' to quit.\n")
    print("Example questions you can ask:")
    print("- Show me all customers from California")
    print("- What are the top 5 products by sales quantity?")
    print("- Find total revenue by customer in 2023")
    print("- List all orders with their customer names and total amounts")
    
    while True:
        user_input = input("\nAsk your question: ").strip()
        if user_input.lower() in ["exit", "quit"]:
            break

        try:
            # Generate SQL from user input using invoke
            result = chain.invoke({"input": user_input})
            print("\nGenerated Response:")
            print(result["text"].strip())
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
