import sqlite3

def init_db():
    conn = sqlite3.connect('database.db')
    print("Opened database successfully")

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
    print("Table users created successfully")

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
    print("Table products created successfully")

    conn.execute('''CREATE TABLE IF NOT EXISTS cart
            (userId INTEGER,
            productId INTEGER,
            FOREIGN KEY(userId) REFERENCES users(userId),
            FOREIGN KEY(productId) REFERENCES products(productId)
            )''')
    print("Table cart created successfully")

    conn.execute('''CREATE TABLE IF NOT EXISTS categories
            (categoryId INTEGER PRIMARY KEY,
            name TEXT
            )''')
    print("Table categories created successfully")

    conn.close()

if __name__ == '__main__':
    init_db()
