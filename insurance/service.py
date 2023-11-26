from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, Flask, send_from_directory, jsonify, session
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

#overall 进行选择去管理端还是客户端
@bp.route('/')
def overall():
    
    return render_template('service/overall.html')

#index
@bp.route('/index')
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
        session['insurance_id'] = insurance_id
        
        db = get_db()
        db.execute(
            'INSERT INTO person (person_idcard, company_name, crime_id, insurance_id, user_id)'
            ' VALUES (?, ?, ?, ?, ?)',
            (person_idcard, company_name, crime_id, insurance_id, g.user['id'])
        )
        db.commit()
        
        person = db.execute(
            'SELECT id FROM person WHERE insurance_id = ?',
            (insurance_id,)
        ).fetchone()
        
        db.execute(
            'INSERT INTO service (service_insurance, service_id)'
            ' VALUES (?, ?)',
            (insurance_id, person['id'])
        )
        db.commit()
        return redirect(url_for('service.upload_material'))
        
    return render_template('service/Report-crime.html') 

@bp.route('/material_upload', methods=("GET", "POST"))
@login_required
def upload_material():
    insurance_id = session.get('insurance_id')
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
#最主要的问题在这里，解决方案就是从上面获取insurance_id 并传到下面来，就完事了，因为insurance_id 是unique，所以这一定是最好的判断条件           
            db.execute(
                'UPDATE service'
                ' SET service_date = ?, service_reason = ?, treatment = ?, service_description = ?, service_hospital = ?'
                ' WHERE service_insurance = ?',
                (service_date, service_reason, treatment, service_description, service_hospital, insurance_id)   
            )
            db.commit()
            
            db.execute(
                'UPDATE person'
                ' SET person_name = ?, person_gender = ?, person_birth = ?, person_phone = ?, person_rephone = ?, person_email = ?'
                ' WHERE insurance_id = ?',
                (person_name, person_gender, person_birth, person_phone, person_rephone, person_email, insurance_id)
            )
            db.commit()
            return redirect(url_for("service.upload_image"))
    
    return render_template('service/upload-material.html')

@bp.route('/image_upload', methods=("GET", "POST"), strict_slashes=False)
@login_required
def upload_image():
    insurance_id = session.get('insurance_id')
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
        
        f_1 = request.files['myfile_1']
        print(f_1)
        if f_1 and allowed_file(f_1.filename):
            fname = f_1.filename
            ext = fname.rsplit('.', 1)[1]
            unix_time = int(time.time()+1)
            filename_part = str(unix_time) + '.' + ext
            f_1.save(os.path.join(file_dir, filename_part))
            
        
        f_2 = request.files['myfile_2']
        if f_2 and allowed_file(f_2.filename):
            fname = f_2.filename
            ext = fname.rsplit('.', 1)[1]
            unix_time = int(time.time()+2)
            filename_accident = str(unix_time) + '.' + ext
            f_2.save(os.path.join(file_dir, filename_accident))
            
    
            path_whole = "../static/upload/" + filename_whole
            path_part = "../static/upload/" + filename_part
            path_accident = "../static/upload/" + filename_accident
            case_status = "待处理"
            case_progress = "请按照要求, 补充上传对应的理赔材料"
            
        db = get_db()
        #这里也一样，将insurance_id 传到下面来就可以了
        db.execute(
            'UPDATE service'
            ' SET image_path_whole = ?, image_path_part = ?, image_path_accident = ?, case_status = ?, case_progress = ?'
            ' WHERE service_insurance = ?',
            (path_whole, path_part, path_accident, case_status, case_progress, insurance_id)
        )
        db.commit()
        #清除session
        session.clear
        return redirect(url_for('service.index'))
            
  
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
    whole_path ="insurance"+path_whole[2:]
    part_path = "insurance" + path_part[2:]
    accident_path = "insurance" + path_accident[2:]
    os.remove(whole_path)
    os.remove(path_part)
    os.remove(accident_path)
    
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
@bp.route('/<int:service_id>/clime_upload', methods=("GET", "POST"))
@login_required
def upload_clime(service_id):
    service_id = service_id
    db = get_db()
    
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
            
        #这里也一样，将insurance_id 传到下面来就可以了
        db.execute(
            'UPDATE service'
            ' SET image_path_whole = ?, image_path_part = ?, image_path_accident = ?'
            ' WHERE service_id = ?',
            (path_whole, path_part, path_accident, service_id)
        )
        db.commit()
        return redirect(url_for('service.index'))
  
    return render_template('service/upload-clime.html')


#错误反应：
@bp.errorhandler(400)
def bad_request(e):
    return render_template('400.html'), 400


@bp.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@bp.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@bp.errorhandler(405)
def method_not_allowed(e):
    # if a request has the wrong method to our API
    if request.path.startswith('/api/'):
        # we return a json saying so
        return jsonify(message="Method Not Allowed"), 405
    else:
        # otherwise we return a generic site-wide 405 page
        return render_template("405.html"), 405

