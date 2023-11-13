from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, Flask, send_from_directory, jsonify
)
from werkzeug.exceptions import abort
from insurance.auth import login_required
from insurance.db import get_db
import time
import os
import random

bp = Blueprint('service', __name__)

basedir = os.path.abspath(os.path.dirname(__file__))  # 获取当前项目的绝对路径
ALLOWED_EXTENSIONS = set(['txt', 'png', 'jpg', 'xls', 'JPG', 'PNG', 'xlsx', 'gif', 'GIF', 'avif'])  # 允许上传的文件后缀

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
@login_required
def report_crime():
    #这里使用查询，为了确保这个人确实有投过保， 还得确保过保多少天后可以报案
    if request.method == 'POST':
        person_idcard = request.form['person_idcard']
        company_name = request.form['company_name']
        
#此处进行对报案号和保单号的自动生成：
        today = time.strftime("%Y%m%d",time.localtime(time.time()))
        charset_word = "ABCDEFGHIGKLMNOPQRSTUVWXYZ"
        charset_num = "012345678901234567890123456789"
        result = random.sample(charset_word, 4)
        result_1 = random.sample(charset_num, 6)
        result_2 = random.sample(charset_word, 1)
        result_3 = random.sample(charset_num, 21)
        
        crime_id = "".join(result) + today + "".join(result_1)
        insurance_id = "".join(result_2) + "".join(result_3)
        db = get_db()
        db.execute(
            'INSERT INTO person (person_idcard, company_name, crime_id, insurance_id, person_id)'
            ' VALUES (?, ?, ?, ?, ?)',
            (person_idcard, company_name, crime_id, insurance_id, g.user['id'])
        )
        db.commit()
        
        return redirect(url_for("service.upload_material"))
    
    return render_template('service/Report-crime.html') 

@bp.route('/material_upload', methods=("GET", "POST"))
@login_required
def upload_material():
    if request.method == 'POST':
        service_date = request.form['service_date']
        service_reason = request.form['service_reason']
        treatment = request.form['treatment']
        service_description = request.form['service_description']
        service_hospital = request.form['service_hospital']
        person_name = request.form['person_name']
        person_gender = request.form['person_gender']
        person_birth = request.form['person_birth']
        person_phone = request.form['person_phone']
        person_rephone = request.form['person_rephone']
        person_email = request.form['person_email']
        error = None
        
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO service (service_date, service_reason, treatment, service_description, service_hospital, service_id)'
                ' VALUES (?, ?, ?, ?, ?, ?)',
                (service_date, service_reason, treatment, service_description, service_hospital, g.user['id'])   
            )
            db.commit()
            db.execute(
                'UPDATE person'
                ' SET person_name = ?, person_gender = ?, person_birth = ?, person_phone = ?, person_rephone = ?, person_email = ?'
                ' WHERE person_id = ?',
                (person_name, person_gender, person_birth, person_phone, person_rephone, person_email, g.user['id'])
            )
            db.commit()
            return redirect(url_for("service.upload_image"))
    
    
    return render_template('service/upload-material.html')

@bp.route('/image_upload', methods=("GET", "POST"), strict_slashes=False)
@login_required
def upload_image():
    # 拼接成合法文件夹地址
    if request.method == "POST":
        file_dir = os.path.join(basedir + "/static", 'upload')    
        f = request.files['myfile']
        if f and allowed_file(f.filename):  # 判断是否是允许上传的文件类型
            fname = f.filename
            ext = fname.rsplit('.', 1)[1]  # 获取文件后缀
            unix_time = int(time.time())
            filename_whole = str(unix_time) + '.' + ext  # 修改文件名
            f.save(os.path.join(file_dir, filename_whole))  # 保存文件到upload目录
            print(filename_whole)
        
        f_1 = request.files['myfile_1']
        if f_1 and allowed_file(f_1.filename):
            fname = f_1.filename
            ext = fname.rsplit('.', 1)[1]
            unix_time = int(time.time()+1)
            filename_part = str(unix_time) + '.' + ext
            f.save(os.path.join(file_dir, filename_part))
            print(filename_part)
        
        f_2 = request.files['myfile_2']
        if f_2 and allowed_file(f_2.filename):
            fname = f_2.filename
            ext = fname.rsplit('.', 1)[1]
            unix_time = int(time.time()+2)
            filename_accident = str(unix_time) + '.' + ext
            f.save(os.path.join(file_dir, filename_accident))
            print(filename_accident)
    
            path_whole = "insurance/static/upload/" + filename_whole
            path_part = "insurance/static/upload/" + filename_part
            path_accident = "insurance/static/upload/" + filename_accident
            
        db = get_db()
        db.execute(
            'UPDATE service'
            ' SET image_path_whole = ?, image_path_part = ?, image_path_accident = ?'
            ' WHERE service_id = ?',
            (path_whole, path_part, path_accident, g.user['id'])
        )
        db.commit()
        return redirect(url_for('service.progress_query'))
            
  
    return render_template('service/upload-image.html')

@bp.route('/example', methods=("GET", "POST"))
@login_required
def material_example():
    return render_template('service/material-example.html')

#query
@bp.route('/query', methods=("GET", "POST"))
@login_required
def progress_query():
    if request.method == "POST":
        query_name = request.form['myquery']
        
        db = get_db()
        services = db.execute(
            'SELECT person_name, service_id, crime_id, insurance_id, service_date, case_progress, case_status'
            ' FROM person p JOIN service s ON p.id = s.service_id'
            ' WHERE person_name = ?',
            (query_name,)
        ).fetchall()
        return render_template('service/Progress-query.html', services = services)
    return render_template('service/Progress-query.html')

#点击块级元素，跳转详细信息,需要撤销就使用delete，还得判断是否为个人用户，不能让别人改其他人的。需要补充就选择使用更新

@bp.route('/<int:service_id>/detail', methods=("GET", "POST"))
@login_required
def query_detail(service_id):
    service_id = service_id
    db = get_db()
    post = db.execute(
        'SELECT person_name, person_gender, person_birth, person_phone, service_date, service_reason, treatment, service_description, crime_id, insurance_id, service_id'
        ' FROM person p JOIN service s ON p.id = s.service_id'
        ' WHERE service_id = ?',
        (service_id,)
    ).fetchone()
    return render_template('service/query-detail.html', post=post)

@bp.route('/<int:service_id>/delete', methods=("GET","POST"))
@login_required
def query_delete(service_id):
    service_id = service_id
    db = get_db()
    
    path = db.execute(
        'SELECT image_path_whole, image_path_part, image_path_accident'
        ' FROM service s'
        ' WHERE service_id = ?',
        (service_id,)
    ).fetchone()
    path_whole = path['image_path_whole']
    path_part = path['image_path_part']
    path_accident = path['image_path_accident']
    os.remove(path_whole)
    os.remove(path_part)
    os.remove(path_accident)
    
    db.execute(
        'DELETE FROM person'
        ' WHERE id = ?',
        (service_id,)
    )
    
    db.execute(
        'DELETE FROM service'
        ' WHERE service_id = ?',
        (service_id,)
    )
    db.commit()
    return redirect(url_for('service.index'))


#提交理赔材料，需要审核后才能提交，如果驳回则需要重新提交
@bp.route('/clime_upload', methods=("GET", "POST"))
@login_required
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


