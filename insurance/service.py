from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, Flask, send_from_directory, jsonify
)
from werkzeug.exceptions import abort
from insurance.auth import login_required
from insurance.db import get_db
import time
import os
bp = Blueprint('service', __name__)

basedir = os.path.abspath(os.path.dirname(__file__))  # 获取当前项目的绝对路径
ALLOWED_EXTENSIONS = set(['txt', 'png', 'jpg', 'xls', 'JPG', 'PNG', 'xlsx', 'gif', 'GIF'])  # 允许上传的文件后缀

#判断是否为合法数据
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

#index
@bp.route('/')
def index():
    #首页记得还需要给管理段一个接口，提供其更改广告标题
    return render_template('service/index.html')

#report crime
@bp.route('/report', methods=('GET', 'POST'))
def report_crime_idcard():
    #这里使用查询，为了确保这个人确实有投过保， 还得确保过保多少天后可以报案
    return render_template('service/Report-crime.html') 

@bp.route('/material_upload', methods=("GET", "POST"))
def upload_material():
    if request.method == 'POST':
        insurance_id = request.form['insurance_id']
        service_date = request.form['service_date']
        service_reason = request.form['service_reason']
        treatment = request.form['treatment']
        service_description = request.form['service_description']
        service_hospital = request.form['service_hospital']
        person_name = request.form['person_name']
        person_phone = request.form['person_phone']
        person_rephone = request.form['person_rephone']
        person_email = request.form['person_email']
        error = None
        
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO service (insurance_id, service_date, service_reason, treatment, service_description, service_hospital, service_id)'
                ' VALUES (?, ?, ?, ?, ?, ?, ?)',
                (insurance_id, service_date, service_reason, treatment, service_description, service_hospital, g.user['id'])   
            )
            db.commit()
            db.execute(
                'INSERT INTO person (person_name, person_phone, person_rephone, person_email, person_id)' 
                ' VALUES (?, ?, ?, ?, ?)',
                (person_name, person_phone, person_rephone, person_email, g.user['id'])
            )
            db.commit()
            return redirect(url_for("service.upload_image"))
    
    
    return render_template('service/upload-material.html')

@bp.route('/image_upload', methods=("GET", "POST"), strict_slashes=False)
def upload_image():
    if request.method == "POST":
        file_dir = os.path.join(basedir, 'upload')  # 拼接成合法文件夹地址
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)  # 文件夹不存在就创建
        f = request.files['myfile']  # 从表单的file字段获取文件，myfile为该表单的name值
        if f and allowed_file(f.filename):  # 判断是否是允许上传的文件类型
            fname = f.filename
            ext = fname.rsplit('.', 1)[1]  # 获取文件后缀
            unix_time = int(time.time())
            new_filename = str(unix_time) + '.' + ext  # 修改文件名
            f.save(os.path.join(file_dir, new_filename))  # 保存文件到upload目录
            return redirect(url_for('service.progress_query'))
  
    return render_template('service/upload-image.html')

@bp.route('/example', methods=("GET", "POST"))
def material_example():
    return render_template('service/material-example.html')

#query
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
        return redirect(url_for('service.progress_query_no'))
    else:
        return redirect(url_for('service.progress_query_something', services=services))
    
    return render_template('service/Progress-query.html')    

@bp.route('/query/nothing')
def progress_query_no():
    return render_template('service/Progress-query-no.html')

@bp.route('/query/something')
def progress_query_something():
    return render_template('service/Progress-query-some.html')

#提交理赔材料，需要审核后才能提交，如果驳回则需要重新提交
@bp.route('/clime_upload', methods=("GET", "POST"))
def upload_clime():
    if request.method == "POST":
        file_dir = os.path.join(basedir, 'upload')  # 拼接成合法文件夹地址
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)  # 文件夹不存在就创建
        f = request.files['myfile']  # 从表单的file字段获取文件，myfile为该表单的name值
        if f and allowed_file(f.filename):  # 判断是否是允许上传的文件类型
            fname = f.filename
            ext = fname.rsplit('.', 1)[1]  # 获取文件后缀
            unix_time = int(time.time())
            new_filename = str(unix_time) + '.' + ext  # 修改文件名
            f.save(os.path.join(file_dir, new_filename))  # 保存文件到upload目录
            return redirect(url_for('service.progress_query'))
  
    return render_template('service/upload-clime.html')

#点击块级元素，跳转详细信息,需要撤销就使用delete，还得判断是否为个人用户，不能让别人改其他人的。需要补充就选择使用更新
@bp.route('/detail', methods=("GET", "POST"))
def query_detail():
    
    return render_template('service/query-detail.html')