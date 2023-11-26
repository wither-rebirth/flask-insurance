from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, Flask, send_from_directory, jsonify, session
)
from werkzeug.exceptions import abort
from werkzeug.security import check_password_hash, generate_password_hash
from insurance.db import get_db
import functools
import time
import os
import re
import random

bp = Blueprint('manage', __name__, url_prefix='/manage')

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.manager is None:
            return redirect(url_for('manage.login'))
        
        return view(**kwargs)
    return wrapped_view

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
            session['manager_id'] = manager['manager_id']
            session['loggedin'] = True
            session['manager_name'] = manager['manager_name']
            session['email'] = manager['manager_email']
            return redirect(url_for("manage.index"))
        
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
            
            return redirect(url_for('manage.login'))
        
        flash(error)
    return render_template('manage/register.html')

@bp.route('/forget', methods=("GET", "POST"))
def forget():
    if request.method == "POST":
        email = request.form['email']
        name = request.form['name']
        error = None
        db = get_db()
        manager = db.execute(
            'SELECT * FROM manager WHERE manager_email = ?', (email,)
        ).fetchone()
        if manager is None:
            error = 'Your account is invalid ! Please enter right email'
        elif email is None:
            error = 'Incorrect email.'
        else:
            return redirect(url_for('manage.change'))
        
        flash(error)
    return render_template('manage/forget.html')

@bp.route('/change', methods=("GET", "POST"))
def change():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        re_password = request.form['re_password']
        error = None
        db = get_db()
        pass_password = db.execute(
            'SELECT *'
            ' FROM manager'
            ' WHERE password = ? and manager_email = ?',
            (generate_password_hash(password), email)
        ).fetchone()
        if password != re_password:
            error = "You need to enter same password from two times"
        elif pass_password :
            error = "This password has existed. Please try other password!"
        else:
            db.execute(
                'UPDATE manager'
                ' SET password = ?'
                ' WHERE manager_email = ?',
                (generate_password_hash(password), email) 
            )
            db.commit()
            return redirect(url_for("manage.login"))
        
        flash(error)
    return render_template('manage/change.html')

@bp.route('/index', methods=("GET", "POST"))
@login_required
def index():
    return render_template('manage/index.html')

@bp.route('/setting', methods=("GET", "POST"))
@login_required
def setting():
    return render_template('manage/setting.html')

@bp.route('/calendar', methods=("GET", "POST"))
@login_required
def calendar():
    
    return render_template('manage/calendar.html')

@bp.route('/chat', methods=("GET", "POST"))
@login_required
def chat():
    return render_template('manage/chat.html')

@bp.route('/ads', methods=("GET", "POST"))
@login_required
def ads():
    
    return render_template('manage/ads_change.html')

#account chart
@bp.route('/account', methods=("GET", "POST"))
@login_required
def account():
    db = get_db()
    accounts = db.execute(
        'SELECT person_name, person_gender, person_birth, person_idcard, crime_id, insurance_id, person_email, person_phone'
        ' FROM person',
    ).fetchall()
    return render_template('manage/account.html', accounts = accounts)

#service chart
@bp.route('service',methods=("GET", "POST"))
@login_required
def service():
    db = get_db()
    services = db.execute(
        'SELECT service_id, person_name, insurance_id, case_status, service_date, service_hospital, treatment, service_reason'
        ' FROM person p JOIN service s ON p.id = s.service_id',
    ).fetchall()
    return render_template("manage/service.html", services = services)

#detail service
@bp.route('/<insurance_id>', methods=("GET", "POST"))
@login_required
def service_detail(insurance_id):
    db = get_db()
    detail = db.execute(
        'SELECT person_name, insurance_id, crime_id, person_gender, person_phone, person_email, image_path_whole, image_path_part, image_path_accident,'
        ' person_birth, person_idcard, company_name, service_date, service_reason, service_hospital, treatment, service_description'
        ' FROM person p JOIN service s on p.id = s.service_id'
        ' WHERE insurance_id = ?',
        (insurance_id,)
    ).fetchone()
    if request.method == "POST":
        case_status = request.form['status']
        case_progress = request.form['progress']
        db.execute(
            'UPDATE service'
            ' SET case_status = ?, case_progress = ?'
            ' WHERE service_insurance = ?',
            (case_status, case_progress, insurance_id)
        )
        db.commit()
        return redirect(url_for('manage.service'))
    return render_template("manage/service_detail.html", detail = detail)

#delete service
@bp.route('/<insurance_id>/delete')
@login_required
def service_delete(insurance_id):
    db = get_db()
    
    path = db.execute(
        'SELECT image_path_whole, image_path_part, image_path_accident'
        ' FROM service s'
        ' WHERE service_insurance = ?',
        (insurance_id,)
    ).fetchone()
    
    if path:
        path_whole = path['image_path_whole']
        path_part = path['image_path_part']
        path_accident = path['image_path_accident']
        whole_path ="insurance"+path_whole[2:]
        part_path = "insurance" + path_part[2:]
        accident_path = "insurance" + path_accident[2:]
        os.remove(whole_path)
        os.remove(part_path)
        os.remove(accident_path)
        
    else:
        pass
    
    db.execute(
        'DELETE FROM person'
        ' WHERE insurance_id = ?',
        (insurance_id,)
    )
    
    db.execute(
        'DELETE FROM service'
        ' WHERE service_insurance = ?',
        (insurance_id,)
    )
    db.commit()
    return redirect(url_for('manage.service'))
    
          
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