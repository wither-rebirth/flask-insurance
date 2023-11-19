from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, Flask, send_from_directory, jsonify, session
)
from werkzeug.exceptions import abort
from werkzeug.security import check_password_hash, generate_password_hash
from insurance.auth import login_required
from insurance.db import get_db
import time
import os
import re
import random

bp = Blueprint('manage', __name__, url_prefix='/manage')

@bp.route('/', methods=('GET', 'POST'))
def view():
    return render_template('manage/view.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        error=None
        manager = db.execute(
            'SELECT * FROM manager WHERE manager_email = ?', (email,)
        ).fetchone()
        if manager is None:
            error = 'Your account is invalid ! Please register'
        elif email is None:
            error = 'Incorrect email.'
        elif not check_password_hash(manager['password'], password):
            error = 'Incorrect password.'
        
        if error is None:
            session.clear()
            session['manager_id'] = manager['manager_id']
            session['loggedin'] = True
            session['manager_name'] = manager['manager_name']
            session['email'] = manager['manager_email']
            return redirect(url_for('index'))
        
        flash(error)
    return render_template('manage/login.html')

@bp.route('/register', methods=("GET", "POST"))
def register():
    message = ""
    
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']
        error = None
        db = get_db()
        
        account = db.execute(
            'SELECT * FROM manager WHERE manager_email = ?', (email,)
        ).fetchall()
        
        if account:
            error = "Account already exists !"
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            error = "Invalid email address !"
        elif not name or not password or not email:
            error = "Please fill out the form !"
        else:
            db.execute(
                'INSERT INTO manager (manager_name, manager_email, password)'
                ' VALUES (?, ?, ?)',
                (name, email, generate_password_hash(password))
            )
            db.commit()
            message = "You have successfully registered !"
            
            #return redirect(url_for('manage.login'))
        
        flash(error)
    return render_template('manage/register.html')

@bp.route('/forget', methods=("GET", "POST"))
def forget():
    return render_template('manage/forget.html')

@bp.route('/index', methods=("GET", "POST"))
def index():
    return render_template('manage/index.html')

@bp.before_app_request
def load_logged_in_manager():
    manager_id = session.get('manager_id')
    
    if manager_id is None:
        g.manager = None
    else:
        g.manager = get_db().execute(
            'SELECT * FROM manager WHERE manager_id = ?', (manager_id,)
        ).fetchone()
    
@bp.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('manager_id', None)
    session.pop('manager_name', None)
    session.pop('email', None)
    return redirect(url_for('index'))
    