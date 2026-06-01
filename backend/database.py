import os
import psycopg2
from psycopg2.extras import RealDictCursor
import sqlite3

# Get database URL from environment variable (for Render)
DATABASE_URL = os.environ.get('DATABASE_URL', '')

def get_db_connection():
    """Get database connection - works with both SQLite and PostgreSQL"""
    
    if DATABASE_URL:
        # Production - PostgreSQL on Render
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        return conn
    else:
        # Local development - SQLite
        conn = sqlite3.connect('inventory.db')
        conn.row_factory = sqlite3.Row
        return conn

def execute_query(conn, query, params=None):
    """Execute a query and return results - works with both databases"""
    if DATABASE_URL:
        # PostgreSQL
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor
    else:
        # SQLite
        if params:
            return conn.execute(query, params)
        else:
            return conn.execute(query)

def fetch_all(conn, query, params=None):
    """Fetch all results from a query"""
    cursor = execute_query(conn, query, params)
    if DATABASE_URL:
        results = cursor.fetchall()
        cursor.close()
        return results
    else:
        return cursor.fetchall()

def fetch_one(conn, query, params=None):
    """Fetch one result from a query"""
    cursor = execute_query(conn, query, params)
    if DATABASE_URL:
        result = cursor.fetchone()
        cursor.close()
        return result
    else:
        return cursor.fetchone()

def init_database():
    """Create tables if they don't exist"""
    conn = get_db_connection()
    
    if DATABASE_URL:
        # PostgreSQL syntax
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                sku TEXT UNIQUE NOT NULL,
                price REAL NOT NULL CHECK (price >= 0),
                quantity INTEGER NOT NULL CHECK (quantity >= 0)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                customer_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL CHECK (quantity > 0),
                total_amount REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        ''')
        conn.commit()
        cursor.close()
    else:
        # SQLite syntax
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                sku TEXT UNIQUE NOT NULL,
                price REAL NOT NULL CHECK (price >= 0),
                quantity INTEGER NOT NULL CHECK (quantity >= 0)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL CHECK (quantity > 0),
                total_amount REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        ''')
        conn.commit()
        cursor.close()
    
    conn.close()
    print("Database initialized successfully!")