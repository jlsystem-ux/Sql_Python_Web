from flask import Flask, render_template, request, session, redirect, url_for, flash, jsonify, g
import sqlite3
import os
from functools import wraps
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
# Use a secure secret key. In production, this should be an environment variable.
# Fixed key for development to persist sessions across restarts.
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-prod')
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'jpeg', 'jpg', 'png', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DATABASE'] = 'database.db'

# Lesson Data
lessons_data = {
    1: {
        "title": "Introducción a SQL",
        "content": "SQL (Structured Query Language) es el lenguaje estándar para gestionar bases de datos relacionales. En esta lección aprenderás qué es una base de datos, una tabla y cómo realizar tu primera consulta.",
        "examples": [
            {"title": "Tu primera consulta", "code": "SELECT * FROM users;"}
        ]
    },
    2: {
        "title": "Consultas Básicas",
        "content": "La sentencia SELECT es la más importante en SQL. Te permite recuperar datos de una o más tablas. Aprenderemos a seleccionar columnas específicas.",
        "examples": [
            {"title": "Seleccionar columnas específicas", "code": "SELECT firstName, email FROM users;"}
        ]
    },
    3: {
        "title": "Filtrado de Datos",
        "content": "La cláusula WHERE te permite filtrar resultados para obtener solo los datos que cumplen con ciertas condiciones.",
        "examples": [
            {"title": "Filtrar por ID", "code": "SELECT * FROM users WHERE userId = 1;"}
        ]
    }
}

challenges_data = {
    1: {
        "title": "Seleccionar Todos los Usuarios",
        "description": "Recupera todas las columnas de la tabla 'users'.",
        "difficulty": "Básico",
        "solution_query": "SELECT * FROM users",
        "hint": "Usa SELECT * FROM nombre_tabla"
    },
    2: {
        "title": "Nombres de Productos",
        "description": "Obtén solo el nombre (name) y el precio (price) de todos los productos.",
        "difficulty": "Básico",
        "solution_query": "SELECT name, price FROM products",
        "hint": "Especifica las columnas separadas por coma: SELECT col1, col2 FROM..."
    },
    3: {
        "title": "Productos Caros",
        "description": "Encuentra todos los productos que cuesten más de 20 dólares.",
        "difficulty": "Intermedio",
        "solution_query": "SELECT * FROM products WHERE price > 20",
        "hint": "Usa la cláusula WHERE con el operador >"
    }
}

@app.teardown_appcontext
def close_connection(exception):
    """Close the database connection at the end of the request."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def get_db():
    """Get a database connection from the global context or create a new one."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row
    return db

def login_required(f):
    """Decorator to require login for specific routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' not in session:
            return redirect(url_for('loginForm'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Fetch current user details if logged in."""
    if 'email' not in session:
        return None
    
    db = get_db()
    try:
        cur = db.cursor()
        cur.execute("SELECT userId, firstName, email FROM users WHERE email = ?", (session['email'],))
        user = cur.fetchone()
        return user
    except sqlite3.Error:
        return None

def get_cart_count(user_id):
    """Get the number of items in the user's cart."""
    if not user_id:
        return 0
    db = get_db()
    try:
        cur = db.cursor()
        cur.execute("SELECT count(productId) FROM cart WHERE userId = ?", (user_id,))
        result = cur.fetchone()
        return result[0] if result else 0
    except sqlite3.Error:
        return 0

@app.context_processor
def inject_user():
    """Inject user details into all templates."""
    user = get_current_user()
    if user:
        return dict(loggedIn=True, firstName=user['firstName'], noOfItems=get_cart_count(user['userId']))
    return dict(loggedIn=False, firstName='', noOfItems=0)

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Home page
@app.route("/")
def root():
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT productId, name, price, description, image, stock FROM products')
    itemData = cur.fetchall()
    cur.execute('SELECT categoryId, name FROM categories')
    categoryData = cur.fetchall()
    
    return render_template('home.html', itemData=itemData, categoryData=categoryData)

@app.route("/lesson/<int:lesson_id>")
def lesson(lesson_id):
    lesson = lessons_data.get(lesson_id)
    if not lesson:
        return render_template('generic_page.html', title="Lección no encontrada", content="La lección que buscas no existe."), 404
    return render_template('lesson.html', title=lesson['title'], content=lesson['content'], examples=lesson['examples'])

# Display all items of a category
@app.route("/displayCategory")
def displayCategory():
    categoryId = request.args.get("categoryId")
    
    db = get_db()
    cur = db.cursor()
    # Parameterized query to prevent injection
    cur.execute("""
        SELECT products.productId, products.name, products.price, products.image, categories.name 
        FROM products, categories 
        WHERE products.categoryId = categories.categoryId AND categories.categoryId = ?
    """, (categoryId,))
    data = cur.fetchall()
        
    categoryName = data[0]['name'] if data else "Category"

    return render_template('displayCategory.html', data=data, categoryName=categoryName)

@app.route("/exercise/<int:exercise_id>")
def exercise(exercise_id):
    exercise = challenges_data.get(exercise_id)
    if not exercise:
        return render_template('404.html'), 404
    return render_template('exercise.html', exercise=exercise, exercise_id=exercise_id)

@app.route("/validate-query", methods=["POST"])
@login_required
def validate_query():
    data = request.get_json()
    user_query = data.get('query')
    exercise_id = data.get('exerciseId')
    
    if not user_query or not exercise_id:
        return jsonify({'error': 'Faltan datos'}), 400
        
    exercise = challenges_data.get(int(exercise_id))
    if not exercise:
        return jsonify({'error': 'Ejercicio no encontrado'}), 404

    conn = get_db()
    try:
        cur = conn.cursor()
        
        # 1. Execute User Query
        cur.execute(user_query)
        user_rows = cur.fetchall()
        user_columns = [description[0] for description in cur.description]
        user_results = [dict(zip(user_columns, row)) for row in user_rows]
        
        # 2. Execute Solution Query
        cur.execute(exercise['solution_query'])
        solution_rows = cur.fetchall()
        solution_columns = [description[0] for description in cur.description]
        solution_results = [dict(zip(solution_columns, row)) for row in solution_rows]
        
        # 3. Compare Results
        is_correct = (user_results == solution_results)
        
        message = "¡Correcto! Has resuelto el ejercicio." if is_correct else "Los resultados no coinciden con la solución esperada."
        
        return jsonify({
            'correct': is_correct,
            'message': message,
            'user_results': user_results,
            'user_columns': user_columns
        })
        
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 400
    finally:
        conn.close()

@app.route("/account/profile")
@login_required
def profileHome():
    return render_template("profileHome.html")

@app.route("/account/profile/edit")
@login_required
def editProfile():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT userId, email, firstName, lastName, address1, zipcode, city, state, country, phone FROM users WHERE email = ?", (session['email'],))
    profileData = cur.fetchone()
    return render_template("editProfile.html", profileData=profileData)

@app.route("/account/profile/changePassword", methods=["GET", "POST"])
@login_required
def changePassword():
    if request.method == "POST":
        oldPassword = request.form['oldpassword']
        newPassword = request.form['newpassword']
        
        db = get_db()
        try:
            cur = db.cursor()
            cur.execute("SELECT userId, password FROM users WHERE email = ?", (session['email'],))
            user = cur.fetchone()
            
            if user and check_password_hash(user['password'], oldPassword):
                new_hashed = generate_password_hash(newPassword)
                cur.execute("UPDATE users SET password = ? WHERE userId = ?", (new_hashed, user['userId']))
                db.commit()
                msg = "Changed successfully"
            else:
                msg = "Wrong password"
        except sqlite3.Error:
            db.rollback()
            msg = "Failed"
            
        return render_template("changePassword.html", msg=msg)
    else:
        return render_template("changePassword.html")

@app.route("/updateProfile", methods=["GET", "POST"])
@login_required
def updateProfile():
    if request.method == 'POST':
        email = request.form['email']
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        address1 = request.form['address1']
        zipcode = request.form['zipcode']
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']
        phone = request.form['phone']
        
        db = get_db()
        try:
            cur = db.cursor()
            cur.execute("""
                UPDATE users 
                SET firstName = ?, lastName = ?, address1 = ?, zipcode = ?, city = ?, state = ?, country = ?, phone = ? 
                WHERE email = ?
            """, (firstName, lastName, address1, zipcode, city, state, country, phone, email))
            db.commit()
            msg = "Saved Successfully"
        except sqlite3.Error:
            db.rollback()
            msg = "Error occured"
        return redirect(url_for('editProfile'))

@app.route("/loginForm")
def loginForm():
    if 'email' in session:
        return redirect(url_for('root'))
    else:
        return render_template('login.html', error='')

@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT email, password FROM users WHERE email = ?", (email,))
        user = cur.fetchone()
        
        # Check password hash
        if user and check_password_hash(user['password'], password):
            session['email'] = email
            return redirect(url_for('root'))
        else:
            error = 'Invalid UserId / Password'
            return render_template('login.html', error=error)
            
    return render_template('login.html')

@app.route("/productDescription")
def productDescription():
    productId = request.args.get('productId')
    
    if not productId:
        return redirect(url_for('root'))
        
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT productId, name, price, description, image, stock FROM products WHERE productId = ?', (productId,))
    productData = cur.fetchone()
    
    if not productData:
        flash('Producto no encontrado', 'error')
        return redirect(url_for('root'))
        
    return render_template("productDescription.html", data=productData)

@app.route("/addToCart")
@login_required
def addToCart():
    productId = int(request.args.get('productId'))
    db = get_db()
    try:
        cur = db.cursor()
        cur.execute("SELECT userId FROM users WHERE email = ?", (session['email'],))
        userId = cur.fetchone()[0]
        
        cur.execute("SELECT stock from products WHERE productId = ?", (productId,))
        number_in_stock = int(cur.fetchone()[0])
        
        cur.execute("INSERT INTO cart (userId, productId) VALUES (?, ?)", (userId, productId))
        cur.execute("UPDATE products SET stock = ? WHERE productId = ?", (number_in_stock-1, productId))
        db.commit()
        msg = "Added successfully"
    except sqlite3.Error:
        db.rollback()
        msg = "Error occured"
    return redirect(url_for('root'))

@app.route("/cart")
@login_required
def cart():
    email = session['email']
    
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT userId FROM users WHERE email = ?", (email,))
    userId = cur.fetchone()[0]
    cur.execute("""
        SELECT products.productId, products.name, products.price, products.image 
        FROM products, cart 
        WHERE products.productId = cart.productId AND cart.userId = ?
    """, (userId,))
    products = cur.fetchall()
        
    totalPrice = 0
    for row in products:
        totalPrice += row['price']
    return render_template("cart.html", products=products, totalPrice=totalPrice)

@app.route("/checkout")
@login_required
def checkout():
    email = session['email']
    
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT userId FROM users WHERE email = ?", (email,))
    userId = cur.fetchone()[0]
    cur.execute("""
        SELECT products.productId, products.name, products.price, products.image 
        FROM products, cart 
        WHERE products.productId = cart.productId AND cart.userId = ?
    """, (userId,))
    products = cur.fetchall()
        
    totalPrice = 0
    for row in products:
        totalPrice += row['price']
    return render_template("checkout.html", products=products, totalPrice=totalPrice)

@app.route("/payment")
@login_required
def payment():
    email = session['email']
    
    db = get_db()
    try:
        cur = db.cursor()
        cur.execute("SELECT userId FROM users WHERE email = ?", (email,))
        userId = cur.fetchone()[0]
        cur.execute("DELETE FROM cart WHERE userId = ?", (userId,))
        db.commit()
        msg = "removed successfully"
    except sqlite3.Error:
        db.rollback()
        msg = "error occured"
    return render_template("payment.html")

@app.route("/removeFromCart")
@login_required
def removeFromCart():
    email = session['email']
    productId = int(request.args.get('productId'))
    
    db = get_db()
    try:
        cur = db.cursor()
        cur.execute("SELECT userId FROM users WHERE email = ?", (email,))
        userId = cur.fetchone()[0]
        
        cur.execute("SELECT stock from products WHERE productId = ?", (productId,))
        number_in_stock = int(cur.fetchone()[0])
        
        cur.execute("DELETE FROM cart WHERE userId = ? AND productId = ?", (userId, productId))
        cur.execute("UPDATE products SET stock = ? WHERE productId = ?", (number_in_stock+1, productId))
        db.commit()
        msg = "removed successfully"
    except sqlite3.Error:
        db.rollback()
        msg = "error occured"
    return redirect(url_for('root'))

@app.route("/logout")
def logout():
    session.pop('email', None)
    return redirect(url_for('root'))

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            # Parse form data    
            password = request.form['password']
            email = request.form['email']
            firstName = request.form['firstName']
            lastName = request.form['lastName']
            address1 = request.form['address1']
            zipcode = request.form['zipcode']
            city = request.form['city']
            state = request.form['state']
            country = request.form['country']
            phone = request.form['phone']

            db = get_db()
            cur = db.cursor()
            # Check if email already exists
            cur.execute('SELECT * FROM users WHERE email = ?', (email,))
            if cur.fetchone() is not None:
                return render_template("register.html", error="Email already registered")
            
            # Insert new user with hashed password
            hashed_password = generate_password_hash(password)
            cur.execute('INSERT INTO users (password, email, firstName, lastName, address1, zipcode, city, state, country, phone) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', 
                      (hashed_password, email, firstName, lastName, address1, zipcode, city, state, country, phone))
            db.commit()
            return render_template("login.html", success="Registration successful! Please login.")
                
        except sqlite3.Error as e:
            return render_template("register.html", error="Database error: " + str(e))
        except Exception as e:
            return render_template("register.html", error="An error occurred during registration")
            
    return redirect(url_for('registrationForm'))

@app.route("/registrationForm")
def registrationForm():
    return render_template("register.html")

@app.route("/execute-sql", methods=['POST'])
def execute_sql():
    if 'email' not in session:
        return jsonify({'error': 'Debes iniciar sesión para ejecutar consultas'}), 401
        
    try:
        query = request.json.get('query', '')
        if not query:
            return jsonify({'error': 'La consulta no puede estar vacía'}), 400
            
        db = get_db()
        cur = db.cursor()
        cur.execute(query)
        
        # Obtener los resultados
        rows = cur.fetchall()
        
        # Convertir los resultados a una lista de diccionarios
        results = []
        for row in rows:
            results.append(dict(row))
            
        # Obtener los nombres de las columnas
        columns = [description[0] for description in cur.description] if cur.description else []
        
        return jsonify({
            'success': True,
            'columns': columns,
            'results': results
        })
            
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
