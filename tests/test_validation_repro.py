import pytest
from main import app, get_db

import tempfile
import os

@pytest.fixture
def client():
    db_fd, db_path = tempfile.mkstemp()
    app.config['TESTING'] = True
    app.config['DATABASE'] = db_path
    
    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client
    
    os.close(db_fd)
    os.unlink(db_path)

def init_db():
    db = get_db()
    # Create tables for testing
    db.execute('''
        CREATE TABLE IF NOT EXISTS users (
            userId INTEGER PRIMARY KEY,
            email TEXT,
            firstName TEXT,
            lastName TEXT,
            password TEXT,
            address1 TEXT,
            zipcode TEXT,
            city TEXT,
            state TEXT,
            country TEXT,
            phone TEXT
        )
    ''')
    db.execute('''
        CREATE TABLE IF NOT EXISTS products (
            productId INTEGER PRIMARY KEY,
            name TEXT,
            price REAL,
            description TEXT,
            image TEXT,
            stock INTEGER,
            categoryId INTEGER
        )
    ''')
    # Insert dummy data
    db.execute("INSERT INTO users (email, firstName) VALUES ('test@test.com', 'TestUser')")
    db.execute("INSERT INTO products (name, price) VALUES ('TestProduct', 10.0)")
    db.commit()

def test_validate_query_success(client):
    response = client.post('/validate-query', json={
        'query': 'SELECT * FROM users',
        'exerciseId': 1
    })
    print(f"\nResponse Status: {response.status_code}")
    print(f"Response Data: {response.get_json()}")
    assert response.status_code == 200
    assert response.get_json()['correct'] == True

def test_validate_query_failure(client):
    response = client.post('/validate-query', json={
        'query': 'SELECT * FROM products', # Wrong table for exercise 1
        'exerciseId': 1
    })
    print(f"\nResponse Status: {response.status_code}")
    print(f"Response Data: {response.get_json()}")
    assert response.status_code == 200
    assert response.get_json()['correct'] == False
