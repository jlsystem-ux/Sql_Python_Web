import sqlite3

def seed_db():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    # Seed Categories
    categories = [
        (1, 'Ropa'),
        (2, 'Zapatos'),
        (3, 'Accesorios')
    ]
    
    print("Seeding categories...")
    for cat in categories:
        try:
            cur.execute("INSERT INTO categories (categoryId, name) VALUES (?, ?)", cat)
        except sqlite3.IntegrityError:
            print(f"Category {cat[1]} already exists.")

    # Seed Products
    products = [
        (1, 'Camiseta Python', 25.00, 'Camiseta de algodón con logo de Python', 'shirt.jpg', 100, 1),
        (2, 'Taza SQL', 15.00, 'Taza para café con consultas SQL', 'mug.jpg', 50, 3),
        (3, 'Zapatillas Coder', 80.00, 'Zapatillas cómodas para largas sesiones de código', 'shoes.jpg', 20, 2),
        (4, 'Gorra Debugger', 20.00, 'Gorra para protegerte de los bugs', 'hat.jpg', 75, 3),
        (5, 'Hoodie Flask', 45.00, 'Sudadera con capucha de Flask', 'hoodie.jpg', 60, 1)
    ]

    print("Seeding products...")
    for prod in products:
        try:
            cur.execute("INSERT INTO products (productId, name, price, description, image, stock, categoryId) VALUES (?, ?, ?, ?, ?, ?, ?)", prod)
        except sqlite3.IntegrityError:
            print(f"Product {prod[1]} already exists.")

    conn.commit()
    conn.close()
    print("Database seeded successfully!")

if __name__ == '__main__':
    seed_db()
