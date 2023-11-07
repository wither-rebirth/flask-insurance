from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from insurance.auth import login_required
from insurance.db import get_db

bp = Blueprint('service', __name__)

@bp.route('/')
def index():
    
    return render_template('service/index.html')

@bp.route('/report', methods=('GET', 'POST'))
def report_crime_idcard():
    return render_template('service/Report-crime.html') 
    
    '''
    if request.method == 'POST':
        person_idcard = request.form['person_idcard']
        error = None
        
        if not person_idcard:
            error = 'personal idcard is required'
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO person (person_idcard)'
                ' VALUES (?)',
                (person_idcard,)
            )  
            db.commit()  
       
        return redirect(url_for('service.index'))
        
         
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
                'INSERT INTO person (person_name, company_name, person_id)'
                ' VALUES (?, ?, ?)',
                (person_name, company_name, g.user['id'])
            )  
            db.commit()  
            return redirect(url_for('service.index'))
        
    return render_template('service/Report-crime.html')
'''
@bp.route('/query', methods=("GET", "POST"))
def progress_query():
    crime_id = request.form.get('crime_id')
    db = get_db()
    services = db.execute(
        'SELECT p.id, p.person_name, crime_id, insurance_id, service_date, case_progress, case_status'
        ' FROM person p JOIN service s ON p.id = s.service_id'
        ' WHERE p.person_name = ?',
        (crime_id,)
    ).fetchone()
    if services is None :
        return render_template('service/Progress-query-no.html')
    else:
        return render_template('service/Progress-query-some.html', services=services)
    
    return render_template('service/Progress-query.html')    

'''
@bp.route('/query/nothing')
def progress_query_no():
    return render_template('service/Progress-query-no.html')

@bp.route('/query/something')
def progress_query_something():
    return render_template('service/Progress-query-some.html')

'''
@bp.route('/example', methods=("GET", "POST"))
def material_example():
    return render_template('service/material-example.html')

@bp.route('/detail', methods=("GET", "POST"))
def query_detail():
    return render_template('service/query-detail.html')

@bp.route('/image_upload', methods=("GET", "POST"))
def upload_image():
    return render_template('service/upload-image.html')

@bp.route('/material_upload', methods=("GET", "POST"))
def upload_material():
    return render_template('service/upload-material.html')

@bp.route('/clime_upload', methods=("GET", "POST"))
def upload_clime():
    return render_template('service/upload-clime.html')