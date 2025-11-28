import pytest
import sqlite3
import os
import tempfile
from main import app

@pytest.fixture
def client():
    # Create a temporary file to isolate the database for each test run
    db_fd, db_path = tempfile.mkstemp()
    
    app.config['TESTING'] = True
    app.config['DATABASE'] = db_path
    app.secret_key = 'test-secret-key'

    # Initialize the database with schema
    # We need to replicate the schema creation here since database.py is not easily importable/configurable
    conn = sqlite3.connect(db_path)
    conn.execute('''CREATE TABLE IF NOT EXISTS users 
            (userId INTEGER PRIMARY KEY, 
            password TEXT,
            email TEXT,
            firstName TEXT,
            lastName TEXT,
            address1 TEXT,
            zipcode TEXT,
            city TEXT,
            state TEXT,
            country TEXT, 
            phone TEXT
            )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS products
            (productId INTEGER PRIMARY KEY,
            name TEXT,
            price REAL,
            description TEXT,
            image TEXT,
            stock INTEGER,
            categoryId INTEGER,
            FOREIGN KEY(categoryId) REFERENCES categories(categoryId)
            )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS cart
            (userId INTEGER,
            productId INTEGER,
            FOREIGN KEY(userId) REFERENCES users(userId),
            FOREIGN KEY(productId) REFERENCES products(productId)
            )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS categories
            (categoryId INTEGER PRIMARY KEY,
            name TEXT
            )''')
    conn.commit()
    conn.close()

    with app.test_client() as client:
        with app.app_context():
            yield client

    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)
