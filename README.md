# Natural Language to SQL Query System

This project provides an intelligent interface for querying a retail store database using natural language. It offers two different approaches: a simple text-to-SQL converter and a more advanced LangChain SQL agent.

## Project Structure

```
Agentic_AI/
  ├── create_database.py    # Database initialization script
  ├── data/                 # CSV data files
  │   ├── customers.csv
  │   ├── orders.csv
  │   ├── products.csv
  │   └── sales.csv
  ├── langchain_sql_agent.py # Advanced SQL agent implementation
  ├── requirements.txt       # Project dependencies
  ├── retail_store.db       # SQLite database
  └── text_to_sql.py        # Simple text-to-SQL converter
```

## Prerequisites

-   Python 3.8 or higher
-   Together AI API key (sign up at [Together AI](https://www.together.ai/))

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd Agentic_AI
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root and add your Together AI API key:

```
TOGETHER_API_KEY=your_api_key_here
```

## Setup and Usage

### 1. Database Creation (Required First Step)

Before using any of the query interfaces, you must first create and populate the database:

```bash
python create_database.py
```

This script will:

-   Create a SQLite database (`retail_store.db`)
-   Create tables for customers, products, orders, and sales
-   Import data from the CSV files in the `data/` directory
-   Display the database schema

### 2. Choose Your Query Interface

You have two options for querying the database:

#### Option 1: Simple Text-to-SQL Converter

```bash
python text_to_sql.py
```

This interface:

-   Converts natural language to optimized SQL queries
-   Provides explanations for the generated queries
-   Focuses on query optimization and readability

#### Option 2: Advanced LangChain SQL Agent

```bash
python langchain_sql_agent.py
```

This interface:

-   Provides a more interactive and dynamic query experience
-   Can handle complex, multi-step queries
-   Includes additional tools for database interaction
-   Offers more detailed responses and explanations

## Database Schema

The retail store database consists of four main tables:

1. **customers**

    - customer_id (Primary Key)
    - name, email, gender, address, city, state

2. **products**

    - product_id (Primary Key)
    - product_name, description, price, stock_quantity, category

3. **orders**

    - order_id (Primary Key)
    - customer_id (Foreign Key)
    - order_date, payment

4. **sales**
    - sale_id (Primary Key)
    - order_id (Foreign Key)
    - product_id (Foreign Key)
    - quantity, unit_price, total_price

## Example Queries

You can ask questions like:

-   "Show me all customers from California"
-   "What are the top 5 products by sales quantity?"
-   "Find total revenue by customer in 2023"
-   "List all orders with their customer names and total amounts"

## Requirements

```
python-dotenv>=1.0.0
langchain>=0.1.0
langchain-openai>=0.0.2
tabulate
pandas
sqlite3
```

## Notes

-   The system uses the Llama 3.3 70B Instruct Turbo model through Together AI's API
-   All database operations are performed on a local SQLite database
-   The system includes built-in schema awareness for accurate query generation
-   Both interfaces provide detailed explanations of generated queries

## Error Handling

Both interfaces include robust error handling for:

-   Database connection issues
-   Invalid queries
-   API authentication problems
-   Malformed user input

## Contributing

Feel free to submit issues and enhancement requests!
