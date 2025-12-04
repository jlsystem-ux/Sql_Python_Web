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

# SQL Learning Categories
categories_data = [
    {"id": 1, "name": "SQL Fundamentals", "description": "SELECT, WHERE, ORDER BY, LIMIT"},
    {"id": 2, "name": "Filtering & Sorting", "description": "AND/OR/NOT, IN, BETWEEN, LIKE"},
    {"id": 3, "name": "Aggregate Functions", "description": "COUNT, SUM, AVG, GROUP BY, HAVING"},
    {"id": 4, "name": "Joins & Relationships", "description": "INNER JOIN, LEFT JOIN, RIGHT JOIN"},
    {"id": 5, "name": "Subqueries", "description": "Nested queries, IN, EXISTS"},
    {"id": 6, "name": "Advanced Queries", "description": "UNION, CTEs, Window functions"},
    {"id": 7, "name": "Data Manipulation", "description": "INSERT, UPDATE, DELETE"},
    {"id": 8, "name": "Database Objects", "description": "Views, Indexes, Triggers"},
]

# Lesson Data
lessons_data = {
    # SQL Fundamentals
    1: {
        "title": "Introducción a SELECT",
        "category": "SQL Fundamentals",
        "content": "SELECT es la instrucción más fundamental en SQL. Te permite recuperar datos de una o más tablas. Aprenderás a seleccionar todas las columnas o columnas específicas.",
        "examples": [
            {"title": "Seleccionar todo", "code": "SELECT * FROM employees;"},
            {"title": "Columnas específicas", "code": "SELECT first_name, last_name, email FROM employees;"},
        ]
    },
    2: {
        "title": "WHERE - Filtrado Básico",
        "category": "SQL Fundamentals",
        "content": "La cláusula WHERE te permite filtrar resultados para obtener solo los datos que cumplen ciertas condiciones.",
        "examples": [
            {"title": "Filtrar por valor", "code": "SELECT * FROM employees WHERE department_id = 2;"},
            {"title": "Comparación numérica", "code": "SELECT * FROM employees WHERE salary > 80000;"},
        ]
    },
    3: {
        "title": "ORDER BY y LIMIT",
        "category": "SQL Fundamentals",
        "content": "ORDER BY ordena los resultados. LIMIT restringe el número de filas devueltas.",
        "examples": [
            {"title": "Ordenar ascendente", "code": "SELECT * FROM employees ORDER BY salary ASC;"},
            {"title": "Top 5 salarios", "code": "SELECT * FROM employees ORDER BY salary DESC LIMIT 5;"},
        ]
    },
    # Filtering & Sorting
    4: {
        "title": "Operadores Lógicos (AND, OR, NOT)",
        "category": "Filtering & Sorting",
        "content": "Combina múltiples condiciones usando AND, OR y NOT para filtros más complejos.",
        "examples": [
            {"title": "AND", "code": "SELECT * FROM employees WHERE department_id = 2 AND salary > 75000;"},
            {"title": "OR", "code": "SELECT * FROM bugs WHERE severity = 'Critical' OR severity = 'High';"},
        ]
    },
    5: {
        "title": "IN, BETWEEN, LIKE",
        "category": "Filtering & Sorting",
        "content": "Operadores especiales para filtrado avanzado: IN para listas, BETWEEN para rangos, LIKE para patrones.",
        "examples": [
            {"title": "IN", "code": "SELECT * FROM bugs WHERE status IN ('Open', 'In Progress');"},
            {"title": "LIKE", "code": "SELECT * FROM employees WHERE email LIKE '%@company.com';"},
        ]
    },
    # Aggregate Functions
    6: {
        "title": "COUNT, SUM, AVG, MIN, MAX",
        "category": "Aggregate Functions",
        "content": "Funciones de agregación calculan valores sobre un conjunto de filas.",
        "examples": [
            {"title": "COUNT", "code": "SELECT COUNT(*) as total_employees FROM employees;"},
            {"title": "AVG", "code": "SELECT AVG(salary) as avg_salary FROM employees;"},
        ]
    },
    7: {
        "title": "GROUP BY y HAVING",
        "category": "Aggregate Functions",
        "content": "GROUP BY agrupa filas con valores similares. HAVING filtra grupos.",
        "examples": [
            {"title": "GROUP BY", "code": "SELECT department_id, COUNT(*) FROM employees GROUP BY department_id;"},
            {"title": "HAVING", "code": "SELECT department_id, AVG(salary) FROM employees GROUP BY department_id HAVING AVG(salary) > 85000;"},
        ]
    },
    # Joins
    8: {
        "title": "INNER JOIN",
        "category": "Joins & Relationships",
        "content": "INNER JOIN combina filas de dos tablas basándose en una condición relacionada.",
        "examples": [
            {"title": "Join básico", "code": "SELECT e.first_name, e.last_name, d.department_name FROM employees e INNER JOIN departments d ON e.department_id = d.department_id;"},
        ]
    },
    9: {
        "title": "LEFT JOIN y RIGHT JOIN",
        "category": "Joins & Relationships",
        "content": "LEFT/RIGHT JOIN devuelve todas las filas de una tabla y las coincidencias de la otra.",
        "examples": [
            {"title": "LEFT JOIN", "code": "SELECT p.project_name, COUNT(ep.employee_id) FROM projects p LEFT JOIN employee_projects ep ON p.project_id = ep.project_id GROUP BY p.project_name;"},
        ]
    },
    # Subqueries
    10: {
        "title": "Subconsultas Básicas",
        "category": "Subqueries",
        "content": "Una subconsulta es una consulta dentro de otra consulta.",
        "examples": [
            {"title": "Subquery en WHERE", "code": "SELECT * FROM employees WHERE salary > (SELECT AVG(salary) FROM employees);"},
        ]
    },
}

challenges_data = {
    # SQL Fundamentals
    1: {
        "title": "Listar Todos los Empleados",
        "description": "Recupera todas las columnas de la tabla 'employees'.",
        "difficulty": "Beginner",
        "category": "SQL Fundamentals",
        "solution_query": "SELECT * FROM employees",
        "hint": "Usa SELECT * FROM nombre_tabla"
    },
    2: {
        "title": "Empleados del Departamento QA",
        "description": "Encuentra todos los empleados que trabajan en el departamento con department_id = 2 (Quality Assurance).",
        "difficulty": "Beginner",
        "category": "SQL Fundamentals",
        "solution_query": "SELECT * FROM employees WHERE department_id = 2",
        "hint": "Usa WHERE para filtrar por department_id"
    },
    3: {
        "title": "Top 5 Salarios Más Altos",
        "description": "Obtén los 5 empleados con los salarios más altos.",
        "difficulty": "Beginner",
        "category": "SQL Fundamentals",
        "solution_query": "SELECT * FROM employees ORDER BY salary DESC LIMIT 5",
        "hint": "Usa ORDER BY salary DESC LIMIT 5"
    },
    # Filtering & Sorting
    4: {
        "title": "Bugs Críticos y Altos",
        "description": "Encuentra todos los bugs con severity 'Critical' o 'High'.",
        "difficulty": "Beginner",
        "category": "Filtering & Sorting",
        "solution_query": "SELECT * FROM bugs WHERE severity IN ('Critical', 'High')",
        "hint": "Usa IN ('Critical', 'High') o severity = 'Critical' OR severity = 'High'"
    },
    5: {
        "title": "Empleados con Email de Compañía",
        "description": "Encuentra todos los empleados cuyo email termina en '@company.com'.",
        "difficulty": "Beginner",
        "category": "Filtering & Sorting",
        "solution_query": "SELECT * FROM employees WHERE email LIKE '%@company.com'",
        "hint": "Usa LIKE con el patrón '%@company.com'"
    },
    # Aggregate Functions
    6: {
        "title": "Contar Empleados por Departamento",
        "description": "Cuenta cuántos empleados hay en cada departamento.",
        "difficulty": "Intermediate",
        "category": "Aggregate Functions",
        "solution_query": "SELECT department_id, COUNT(*) as employee_count FROM employees GROUP BY department_id",
        "hint": "Usa COUNT(*) con GROUP BY department_id"
    },
    7: {
        "title": "Salario Promedio por Departamento",
        "description": "Calcula el salario promedio de cada departamento.",
        "difficulty": "Intermediate",
        "category": "Aggregate Functions",
        "solution_query": "SELECT department_id, AVG(salary) as avg_salary FROM employees GROUP BY department_id",
        "hint": "Usa AVG(salary) con GROUP BY"
    },
    8: {
        "title": "Tests Fallidos por Proyecto",
        "description": "Cuenta cuántos tests han fallado en cada proyecto.",
        "difficulty": "Intermediate",
        "category": "Aggregate Functions",
        "solution_query": "SELECT project_id, COUNT(*) as failed_count FROM test_results WHERE test_status = 'Failed' GROUP BY project_id",
        "hint": "Filtra por test_status = 'Failed' y agrupa por project_id"
    },
    # Joins & Relationships
    9: {
        "title": "Empleados con Nombre de Departamento",
        "description": "Lista todos los empleados junto con el nombre de su departamento.",
        "difficulty": "Intermediate",
        "category": "Joins & Relationships",
        "solution_query": "SELECT e.first_name, e.last_name, d.department_name FROM employees e INNER JOIN departments d ON e.department_id = d.department_id",
        "hint": "Usa INNER JOIN entre employees y departments"
    },
    10: {
        "title": "Proyectos con Conteo de Empleados",
        "description": "Lista todos los proyectos y cuántos empleados están asignados a cada uno.",
        "difficulty": "Intermediate",
        "category": "Joins & Relationships",
        "solution_query": "SELECT p.project_name, COUNT(ep.employee_id) as employee_count FROM projects p LEFT JOIN employee_projects ep ON p.project_id = ep.project_id GROUP BY p.project_name",
        "hint": "Usa LEFT JOIN con employee_projects y GROUP BY"
    },
    # Subqueries
    11: {
        "title": "Empleados con Salario Sobre el Promedio",
        "description": "Encuentra todos los empleados que ganan más que el salario promedio.",
        "difficulty": "Advanced",
        "category": "Subqueries",
        "solution_query": "SELECT * FROM employees WHERE salary > (SELECT AVG(salary) FROM employees)",
        "hint": "Usa una subconsulta: WHERE salary > (SELECT AVG(salary) FROM employees)"
    },
    12: {
        "title": "Bugs Reportados por Testers QA",
        "description": "Encuentra todos los bugs reportados por empleados del departamento de QA (department_id = 2).",
        "difficulty": "Advanced",
        "category": "Subqueries",
        "solution_query": "SELECT * FROM bugs WHERE reported_by IN (SELECT employee_id FROM employees WHERE department_id = 2)",
        "hint": "Usa IN con una subconsulta que filtre employees por department_id"
    },
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
        return dict(loggedIn=True, firstName=user['firstName'], noOfItems=0)
    return dict(loggedIn=False, firstName='', noOfItems=0)

def get_user_progress(user_id):
    """Get set of completed exercise IDs for a user."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT exercise_id FROM user_progress WHERE user_id = ? AND completed = 1', (user_id,))
    return {row[0] for row in cur.fetchall()}

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Home page
@app.route("/")
def root():
    return render_template('home.html', categoryData=categories_data)

@app.route("/category/<int:category_id>")
def category(category_id):
    """Display lessons and exercises for a specific category."""
    # Find the category
    category = next((c for c in categories_data if c['id'] == category_id), None)
    if not category:
        return render_template('404.html'), 404
    
    # Filter lessons and exercises by category
    category_lessons = {k: v for k, v in lessons_data.items() if v.get('category') == category['name']}
    category_exercises = {k: v for k, v in challenges_data.items() if v.get('category') == category['name']}
    
    # Get user progress if logged in
    completed_exercises = set()
    if 'email' in session:
        user = get_current_user()
        if user:
            completed_exercises = get_user_progress(user['userId'])

    return render_template('category.html', 
                         category=category, 
                         lessons=category_lessons, 
                         exercises=category_exercises,
                         completed_exercises=completed_exercises)

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
        
        # 4. Save Progress if Correct
        if is_correct and 'email' in session:
            user = get_current_user()
            if user:
                try:
                    # Check if already completed
                    cur.execute('''
                        SELECT 1 FROM user_progress 
                        WHERE user_id = ? AND exercise_id = ?
                    ''', (user['userId'], int(exercise_id)))
                    
                    if not cur.fetchone():
                        # Record completion
                        cur.execute('''
                            INSERT INTO user_progress (user_id, category_name, lesson_id, exercise_id, completed, completed_at)
                            VALUES (?, ?, ?, ?, 1, datetime('now'))
                        ''', (user['userId'], exercise.get('category', 'General'), 0, int(exercise_id)))
                        conn.commit()
                except Exception as e:
                    print(f"Error saving progress: {e}")

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

@app.route("/profile")
@login_required
def profile():
    user = get_current_user()
    if not user:
        return redirect(url_for('loginForm'))
        
    conn = get_db()
    cur = conn.cursor()
    
    # Get completed exercises count
    cur.execute('SELECT COUNT(*) FROM user_progress WHERE user_id = ? AND completed = 1', (user['userId'],))
    completed_count = cur.fetchone()[0]
    
    # Get total exercises
    total_exercises = len(challenges_data)
    
    # Calculate percentage
    progress_percent = int((completed_count / total_exercises) * 100) if total_exercises > 0 else 0
    
    # Get recent activity
    cur.execute('''
        SELECT category_name, completed_at 
        FROM user_progress 
        WHERE user_id = ? 
        ORDER BY completed_at DESC 
        LIMIT 5
    ''', (user['userId'],))
    recent_activity = cur.fetchall()
    
    return render_template('profile.html', 
                         user=user, 
                         completed_count=completed_count,
                         total_exercises=total_exercises,
                         progress_percent=progress_percent,
                         recent_activity=recent_activity)

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
