import sqlite3
import pandas as pd
import os

def print_schema():
    # Connect to the database
    conn = sqlite3.connect('retail_store.db')
    cursor = conn.cursor()
    
    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print("\nDatabase Schema:")
    print("================")
    
    # For each table, get and print its schema
    for table in tables:
        table_name = table[0]
        print(f"\nTable: {table_name}")
        print("-" * (len(table_name) + 7))
        
        # Get table info
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        
        # Print column information
        for col in columns:
            print(f"Column: {col[1]:<20} Type: {col[2]:<10} {'Primary Key' if col[5] else ''}")
    
    conn.close()

def create_database():
    # Connect to SQLite database (creates a new database if it doesn't exist)
    conn = sqlite3.connect('retail_store.db')
    cursor = conn.cursor()

    # Create customers table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS customers (
        customer_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT,
        gender TEXT,
        address TEXT,
        city TEXT,
        state TEXT
    )
    ''')

    # Create products table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY,
        product_name TEXT NOT NULL,
        description TEXT,
        price DECIMAL(10, 2),
        stock_quantity INTEGER,
        category TEXT
    )
    ''')

    # Create orders table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        order_date DATE,
        payment DECIMAL(10, 2),
        FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
    )
    ''')

    # Create sales table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sales (
        sale_id INTEGER PRIMARY KEY,
        order_id INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        unit_price DECIMAL(10, 2),
        total_price DECIMAL(10, 2),
        FOREIGN KEY (order_id) REFERENCES orders (order_id),
        FOREIGN KEY (product_id) REFERENCES products (product_id)
    )
    ''')

    # Load and insert data from CSV files
    data_dir = 'data'
    
    # Load customers data
    customers_df = pd.read_csv(os.path.join(data_dir, 'customers.csv'))
    customers_df.to_sql('customers', conn, if_exists='replace', index=False)

    # Load products data
    products_df = pd.read_csv(os.path.join(data_dir, 'products.csv'))
    products_df.to_sql('products', conn, if_exists='replace', index=False)

    # Load orders data
    orders_df = pd.read_csv(os.path.join(data_dir, 'orders.csv'))
    orders_df.to_sql('orders', conn, if_exists='replace', index=False)

    # Load sales data
    sales_df = pd.read_csv(os.path.join(data_dir, 'sales.csv'))
    sales_df.to_sql('sales', conn, if_exists='replace', index=False)

    # Commit changes and close connection
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()
    print_schema()
