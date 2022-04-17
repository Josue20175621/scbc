from flask import redirect, session
from functools import wraps

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def format(l):
    _str = ""
    for i in l:
        _str += f"{i[0]}, "
    return _str[:len(_str) - 2]

def format_seat(seat):
    a = ""
    for i in seat:
        a += f"{i[3]}{i[4]}, "
    return a[:len(a) - 2]
    

def format_time(time):
    f_time = time.split()[1]
    hora = int(f_time[:2])
    period = "PM" if hora >= 12 else "AM"
    d_time = f"{hora%12}:{f_time[3:5]} {period}"
    return d_time