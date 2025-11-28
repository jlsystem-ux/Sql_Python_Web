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
DATABASE = 'database.db'

def get_db():
    """Get a database connection from the global context or create a new one."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    """Close the database connection at the end of the request."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

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
    except Exception as e:
        return jsonify({'error': 'Error al ejecutar la consulta'}), 500

@app.route("/lesson<int:lesson_id>")
def lesson(lesson_id):
    titles = {
        1: "Introducción a SQL",
        2: "Consultas Básicas",
        3: "Filtrado de Datos"
    }
    title = titles.get(lesson_id, "Lección")
    content = f"Bienvenido a la lección {lesson_id}. Aquí aprenderás sobre {title}."
    return render_template('lesson.html', title=title, content=content)

@app.route("/joins")
def joins():
    return render_template('lesson.html', title="JOINs", content="Aprende a combinar datos de múltiples tablas.")

@app.route("/subqueries")
def subqueries():
    return render_template('lesson.html', title="Subconsultas", content="Aprende a usar consultas anidadas.")

@app.route("/indexes")
def indexes():
    return render_template('lesson.html', title="Índices", content="Optimiza tus consultas con índices.")

@app.route("/exercises")
def exercises():
    return render_template('generic_page.html', title="Ejercicios", content="Práctica con nuestros ejercicios interactivos.")

@app.route("/resources")
def resources():
    return render_template('generic_page.html', title="Recursos", content="Documentación y guías útiles.")

@app.route("/community")
def community():
    return render_template('generic_page.html', title="Comunidad", content="Únete a otros testers aprendiendo SQL.")

@app.route("/search")
def searchProducts():
    query = request.args.get('searchQuery')
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT productId, name, price, description, image, stock FROM products WHERE name LIKE ?", ('%' + query + '%',))
    data = cur.fetchall()
    data = parse(data)
    return render_template('displayCategory.html', data=data, categoryName=f"Resultados para '{query}'")

if __name__ == '__main__':
    app.run(debug=True)
