from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash #sha256
from helpers import login_required
import sqlite3

app = Flask(__name__)
database = "data.db"

@app.route("/")
def index():
    
    cur = sqlite3.connect(database).cursor()
    
    images = cur.execute("SELECT * FROM images ORDER BY brief").fetchall()

    return render_template('index.html', images=images)

@app.route('/search', methods=["GET", "POST"])
def search():
    """ Buscar peliculas """
    cur = sqlite3.connect(database).cursor()

    if request.method == "POST":
        movie_title = request.form.get("title")

        results = cur.execute("SELECT * FROM images WHERE brief LIKE ?", ('%'+movie_title+'%',)).fetchall()

        # No existen peliculas con ese titulo o que contengan ese titulo
        if len(results) == 0:
            return render_template("search_e.html", title=movie_title)

        return render_template('searchres.html', results=results)

    else:
        return render_template('search.html')

@app.route('/info')
def movie_info():
    """ Informacion de la pelicula"""
    #cur = sqlite3.connect(database).cursor()
    return render_template('info.html')

@app.route('/login', methods=["GET", "POST"])
def login():

    if request.method == "POST":

        cur = sqlite3.connect(database).cursor()

        email = request.form.get('email')
        password = generate_password_hash(request.form.get('password'))

    return render_template('login.html')


@app.route('/register', methods=["GET", "POST"])
def register():

    con = sqlite3.connect(database)
    cur = con.cursor()

    if request.method == "POST":
        
        name = request.form.get('username')
        email = request.form.get('email')
        password = generate_password_hash(request.form.get('password'))

        # Syntactic Sugar
        guardar_usuario(name, email, password)

        return redirect(url_for('login'))

    return render_template('register.html')

def guardar_usuario(name, email, password):

    con = sqlite3.connect(database)
    cur = con.cursor()

    cur.execute("INSERT INTO users (username, email, hash) VALUES (?, ?, ?)", (name, email, password))
    con.commit()
    con.close()