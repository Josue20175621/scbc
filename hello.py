from flask import Flask, flash, jsonify, redirect, render_template, request, session
import sqlite3

app = Flask(__name__)

@app.route("/")
def index():
    
    con = sqlite3.connect('data.db')
    
    cur = con.cursor()
    
    cur.execute("SELECT * FROM images ORDER BY brief")
    images = cur.fetchall()

    return render_template('index.html', images=images)

@app.route('/search', methods=["GET", "POST"])
def search():
    """ Search movies """
    con = sqlite3.connect('data.db')

    cur = con.cursor()

    if request.method == "POST":
        movie_title = request.form.get("title")

        cur.execute("SELECT * FROM images WHERE brief LIKE ?", ('%'+movie_title+'%',))
        results = cur.fetchall()

        # No hay pelicula con ese nombre disponible
        if len(results) == 0:
            


        return render_template('searchres.html', results=results)
    else:
        return render_template('search.html')


