from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from insurance.auth import login_required
from insurance.db import get_db

bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    
    return render_template('service/index.html')

@bp.route('/report', methods=('GET', 'POST'))
def report_crime_idcard():
    if request.method == 'POSR':
        person_idcard = request.form['person_idcard']
        error = None
        
        if not person_idcard:
            error = 'personal idcard is required'
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO person (person_id, person_id)',
                'VALUES (?, ?)',
                (person_idcard, g.user['id'])
            )  
            db.commit()  
            return redirect(url_for('Report-crime.html'))
        
    return render_template('service/Report-crime.html')
            
def report_crime_name():
    if request.method == 'POST':
        person_name = request.form['person_name']
        company_name = request.form['company_name']
        error = None
        
        if not person_name:
            error = 'name is requeired'
        elif not company_name:
            error = 'company name is required'
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO person (person_name, company_name, person_id)',
                'VALUES (?, ?, ?)',
                (person_name, company_name, g.user['id'])
            )  
            db.commit()  
            return redirect(url_for('Report-crime.html'))
        
    return render_template('service/Report-crime.html')

@bp.route('/query', methods=("GET", "POST"))
def progress_query():
        
    return render_template('service/Progress-query.html')

@bp.route('/example', methods=("GET", "POST"))
def material_example():
    
    return render_template('service/material-example.html')

@bp.route('/detail', methods=("GET", "POST"))
def query_detail():
    return render_template('service/query-detail.html')

@bp.route('upload', methods=("GET", "POST"))
def upload_image():
    return render_template('service/upload-image.html')
