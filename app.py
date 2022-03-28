from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash #sha256
from helpers import login_required
import sqlite3

app = Flask(__name__)

# Asegura que los templates se recargen
app.config["TEMPLATES_AUTO_RELOAD"] = True
database = "data.db"

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Usa el sistema de archivo (en vez de cookies firmadas)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/")
def index():
    
    cur = sqlite3.connect(database).cursor()
    
    movies = cur.execute("SELECT * FROM movies ORDER BY title").fetchall()

    return render_template('index.html', movies=movies)

@app.route('/search', methods=["GET", "POST"])
def search():
    """ Buscar peliculas """
    cur = sqlite3.connect(database).cursor()

    if request.method == "POST":
        movie_title = request.form.get("title")

        results = cur.execute("SELECT * FROM movies WHERE title LIKE ?", ('%'+movie_title+'%',)).fetchall()

        # No existen peliculas con ese titulo o que contengan ese titulo
        if len(results) == 0:
            return render_template("search_e.html", title=movie_title)

        return render_template('searchres.html', results=results)
    else:
        return render_template('search.html')

@app.route('/movie/<int:id>')
def movie(id):
    """ Informacion de la pelicula"""
    cur = sqlite3.connect(database).cursor()

    movies = cur.execute("SELECT * FROM movies WHERE id = ?", (id, )).fetchall()

    return render_template('movie.html', movies=movies)

@app.route('/login', methods=["GET", "POST"])
def login():

    # Olvida cualquier id de usuario
    session.clear()

    if request.method == "POST":

        cur = sqlite3.connect(database).cursor()

        email = request.form.get('email')
        password = request.form.get('password')

        res = cur.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchall()

        if len(res) != 1 or not check_password_hash(res[0][4], password):
            return render_template("login_apology.html")

        # Remember which user has logged in
        session["user_id"] = res[0][0]
        session["email"] = res[0][3]

        # Redirect user to home page
        return redirect("/")

    return render_template('login.html')

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route('/register', methods=["GET", "POST"])
def register():

    if request.method == "POST":
        
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = generate_password_hash(request.form.get('password'))

        # Syntactic Sugar
        guardar_usuario(first_name, last_name, email, password)

        return redirect(url_for('login'))

    return render_template('register.html')

def guardar_usuario(first_name, last_name, email, password):

    con = sqlite3.connect(database)
    cur = con.cursor()

    cur.execute("INSERT INTO users (first_name, last_name, email, hash) VALUES (?, ?, ?, ?)", (first_name, last_name, email, password))
    con.commit()
    con.close()