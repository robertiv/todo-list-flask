from flask import (
    Blueprint, render_template, request, url_for, redirect, flash, session, g
)
from werkzeug.security import generate_password_hash, check_password_hash

from .models import User
from todor import db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods = ('GET', 'POST'))
def register():
    if request.method == 'POST':        
        username = request.form['username']
        password = request.form['password']

        user = User(username, generate_password_hash(password))

        error = None
        exists = User.query.filter_by(username = username).first()
        if exists == None:
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('auth.login'))
        else:
            error = f'El usuario {username} ya esta registrado'
        
        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods = ('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
    
        error = None

        #Validar datos
        exists = User.query.filter_by(username = username).first()
        if(exists == None) or not (check_password_hash(exists.password, password)):
            error = 'Usario o password incorrecta'
        else:
            session.clear()
            session['user_id'] = exists.id
            return redirect(url_for('todo.index'))
        
        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if(user_id == None):
        g.user = None
    else:
        g.user = User.query.get_or_404(user_id)

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

import functools
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:            
            return redirect(url_for('auth.login'))
        
        return view(**kwargs)
    
    return wrapped_view