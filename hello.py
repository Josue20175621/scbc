from flask import Flask, flash, jsonify, redirect, render_template, request, session
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

