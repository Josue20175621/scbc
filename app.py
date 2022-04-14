from ssl import ALERT_DESCRIPTION_DECOMPRESSION_FAILURE
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash #sha256
from helpers import format, login_required, format_time
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
    args = request.args
    error = None
    
    # Ordena por categoria
    if args.get("categoria"):
        query = """SELECT id, titulo, poster FROM peliculas JOIN
            generos ON generos.idPelicula = peliculas.id
            WHERE generos.genero = ? """
        peliculas = cur.execute(query, (args.get("categoria"), )).fetchall()
    else:
        peliculas = cur.execute("SELECT id, titulo, poster FROM peliculas ORDER BY titulo").fetchall()
    
    # No hay peliculas con esa categoria
    if len(peliculas) == 0:
        error = f'No hay peliculas en la categoria {args.get("categoria")}'

    return render_template('index.html', peliculas=peliculas, error=error, categoria=args.get("categoria"))

@app.route('/search', methods=["GET", "POST"])
def search():
    """ Buscar peliculas """
    cur = sqlite3.connect(database).cursor()
    results = None
    error = None
    args = request.args

    if args.get("filter") == "director":
        director = args.get("query")
        results = cur.execute("""SELECT peliculas.id, titulo, poster FROM
        peliculas JOIN directores ON peliculas.id = directores.idPelicula JOIN
        personas ON directores.idPersona = personas.id
        WHERE nombre LIKE ? GROUP BY titulo""", ('%'+director+'%',)).fetchall()
        
        error = f"No se encontraron peliculas con director '{director}'"

    elif args.get("filter") == "actor":
        actor = args.get("query")
        results = cur.execute("""SELECT peliculas.id, titulo, poster FROM 
        peliculas JOIN aparece ON peliculas.id = aparece.idPelicula JOIN
        personas ON aparece.idPersona = personas.id
        WHERE nombre LIKE ? GROUP BY titulo""", ('%'+actor+'%',)).fetchall()
        
        error = f"No se encontraron peliculas con actor '{actor}'"

    elif args.get("filter") == "pelicula":
        titulo = args.get("query")
        results = cur.execute("SELECT * FROM peliculas WHERE titulo LIKE ?", ('%'+titulo+'%',)).fetchall()
        
        error = f"No se encontraron peliculas con actor '{titulo}'"

    if error is not None and len(results) != 0:
        error = None

    return render_template('search.html', error=error, results=results)

@app.route('/movie/<int:id>', methods=["GET", "POST"])
def movie(id):
    """ Informacion de la pelicula"""
    cur = sqlite3.connect(database).cursor()
    
    query = """SELECT titulo, year, sinopsis, poster, duracion, clasificacion, idioma, pais  FROM peliculas JOIN
                clasificaciones ON peliculas.id = clasificaciones.idPelicula JOIN
                idiomas ON peliculas.id = idiomas.idPelicula JOIN
                paises ON peliculas.id = paises.idPelicula JOIN
                directores ON peliculas.id = directores.idPelicula
                WHERE peliculas.id = ? GROUP BY titulo"""
    
    info_pelicula = cur.execute(query, (id, )).fetchall()

    query = """SELECT nombre FROM peliculas JOIN
                aparece ON peliculas.id = aparece.idPelicula JOIN
                personas ON aparece.idPersona = personas.id
                WHERE peliculas.id = ? LIMIT 5"""
    
    actores = cur.execute(query, (id, )).fetchall()

    query = """SELECT nombre FROM peliculas JOIN
            directores ON peliculas.id = directores.idPelicula JOIN
            personas ON directores.idPersona = personas.id
            WHERE peliculas.id = ? """

    directores = cur.execute(query, (id, )).fetchall()

    query = """SELECT idioma FROM peliculas JOIN
            idiomas ON idiomas.idPelicula = peliculas.id
            WHERE peliculas.id = ?"""
    
    idiomas = cur.execute(query, (id, )).fetchall()

    # Lista las tandas por orden de tiempo de inicio
    tandas = cur.execute("SELECT * FROM tandas WHERE idPelicula = ? ORDER BY start_time", (id, )).fetchall()

    return render_template('movie.html', info_pelicula=info_pelicula, actores=format(actores), directores=format(directores), idiomas=format(idiomas), tandas=tandas, format_time=format_time)

@app.route('/seats', methods=["GET", "POST"])
def seats():

    msg = None
    
    if request.method == "POST":
        name = request.form.get('movie_name')
        tickets = request.form.get('boletos')
        showing = request.form.get('tanda')
        msg = 'Selecciona tus asientos'
    
    # Usuario no registrado
    if session.get("user_id") is None:
        msg = 'Consultar asientos'

    return render_template('seats.html', n_seats=tickets, movie=name, tanda=showing, msg=msg)

@app.route('/login', methods=["GET", "POST"])
def login():

    error = None

    # Olvida cualquier id de usuario
    session.clear()

    if request.method == "POST":

        cur = sqlite3.connect(database).cursor()

        email = request.form.get('email')
        password = request.form.get('password')

        res = cur.execute("SELECT * FROM usuarios WHERE correo = ?", (email,)).fetchall()

        # El correo no esta en la base de datos o la contraseña no es correcta
        if len(res) != 1 or not check_password_hash(res[0][4], password):
            error = 'Usuario o contraseña es incorrecto'
        else:
            
            if res[0][5] == 0:
                # Remember which user has logged in
                session["user_id"] = res[0][0]
                session["email"] = res[0][3]
            else:
                session["admin_id"] = res[0][0]
                return redirect(url_for('admin'))

            # Redirecciona al usuario a la pagina principal
            flash('Has iniciado sesion satisfactoriamente')
            return redirect(url_for('index'))

    return render_template('login.html', error=error)

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect(url_for('login'))


@app.route('/register', methods=["GET", "POST"])
def register():

    if request.method == "POST":
        
        nombre = request.form.get('first_name')
        apellido = request.form.get('last_name')
        correo = request.form.get('email')
        clave = generate_password_hash(request.form.get('password'))

        guardar_usuario(nombre, apellido, correo, clave)

        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/checkout', methods=["GET", "POST"])
def checkout():

    render_template('checkout.html')

def guardar_usuario(nombre, apellido, correo, clave):

    con = sqlite3.connect(database)
    cur = con.cursor()

    cur.execute("INSERT INTO usuarios (nombre, apellido, correo, hash, tipo) VALUES (?, ?, ?, ?, 0)", (nombre, apellido, correo, clave))
    con.commit()
    con.close()
